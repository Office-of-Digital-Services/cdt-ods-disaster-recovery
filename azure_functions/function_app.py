from datetime import datetime
import json
import logging
import os
import textwrap

import azure.functions as func
import requests

app = func.FunctionApp()

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
FUNCTION_KEY = os.environ.get("AZURE_FUNCTION_KEY")
APPINSIGHTS_API_KEY = os.environ.get("APPINSIGHTS_API_KEY")
PRODUCTION_ALERT_RULE = "msqalert-cdt-pub-vip-ddrc-P-001"


def format_item(key: str, value: str | None) -> str:
    """
    Formats a key-value pair for the Slack message with bolded key.
    Returns "N/A" if the value is None.
    """
    if value is None:
        value = "N/A"
    return f"*{key}*: {value}"


def format_alert_date(date_str: str | None) -> str:
    """
    Parses an ISO date string, truncates milliseconds, and returns a formatted string.
    Returns "N/A" if the date is None or is in an invalid format.
    """
    if not date_str:
        return "N/A"
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return "N/A"


def format_raw_stack(raw_stack: str) -> str:
    """
    Truncate long raw stack traces for better readability in Slack messages.
    Returns the original stack trace if it's short enough.
    """
    stack = textwrap.dedent(raw_stack).strip()
    lines = stack.splitlines()
    if len(lines) > 20:
        first_10_lines = "\n".join(lines[:10])
        last_10_lines = "\n".join(lines[-10:])
        stack = f"{first_10_lines}\n ... \n{last_10_lines}"
    return stack


def validate_function_key(key: str) -> func.HttpResponse | None:
    """
    Validates the function key from the request.
    Returns an HttpResponse if validation fails, None if it succeeds.
    """
    if not key:
        return func.HttpResponse("Missing code authentication.", status_code=401)
    if key != FUNCTION_KEY:
        logging.warning("Invalid code provided.")
        return func.HttpResponse("Unauthorized: invalid code.", status_code=403)
    return None


def fetch_search_results(api_link: str) -> dict:
    """
    Fetches log details from the Search Results API.
    """
    headers = {"x-api-key": APPINSIGHTS_API_KEY}
    try:
        logging.info(f"Fetching log details from API: {api_link}")
        response = requests.get(api_link, headers=headers)
        response.raise_for_status()
        data = response.json()
        data_str = json.dumps(data, indent=2)  # pretty print 2 spaces indent
        if len(data_str) > 10000:  # 1 byte per character, roughly 10KB, Azure limits to 64KB
            data_str = data_str[:10000] + "... [truncated]"
        logging.info(f"Fetched log details: {data_str}")
        return data["tables"][0] if data["tables"] else {}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching log details from API: {e}")
        return {"error": "Failed to fetch log details."}


def select_search_results(data: dict) -> dict:
    """
    Selects specific columns from the full log details data.
    """
    json_columns: list[dict] = data["columns"]
    columns = [col["name"] for col in json_columns]
    rows: list[list[str | None | int]] = data["rows"]

    selected_columns = ["outerMessage", "details"]
    selected_columns_indexes = {col: columns.index(col) for col in selected_columns}

    details = {}
    for row in rows:  # only one row expected but loop anyway
        entry = {col: row[selected_columns_indexes[col]] for col in selected_columns}
        details.update(entry)

    return details


def format_search_results(data: dict) -> str:
    """
    Converts a dictionary into a formatted string with bolded keys for Slack messages.
    """
    if not data:
        return "_No additional details found._\n"
    formatted_lines = []

    message = data.get("outerMessage", "")
    formatted_lines.append(format_item("Message", message))

    details = data.get("details", "")
    try:
        details = json.loads(details)
        if isinstance(details, list):
            details_item = details[0]
            rawstack = details_item.get("rawStack", "")
            stack = format_raw_stack(rawstack)
            formatted_lines.append(f"*Details*:\n```\n{stack}\n```")
        else:
            formatted_lines.append(format_item("Details", details))
    except json.JSONDecodeError:
        formatted_lines.append(format_item("Details", details))

    formatted_message = "\n".join(formatted_lines) + "\n"
    return formatted_message


def get_details_string(data: dict) -> str:
    alert_context = data.get("alertContext", {})
    condition = alert_context.get("condition", {})
    api_link = condition.get("allOf", [{}])[0].get("linkToSearchResultsAPI", "#")
    search_results = fetch_search_results(api_link)
    selected_search_results = select_search_results(search_results) if "error" not in search_results else {}
    details_str = format_search_results(selected_search_results)
    return details_str


def build_slack_message(data: dict, details: str) -> str:
    """
    Builds the Slack message string from the alert data.
    """
    # See https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-common-schema for available fields
    essentials = data.get("essentials", {})
    alert_id = essentials.get("alertId", "N/A")
    alert_rule = essentials.get("alertRule", "N/A")
    emoji_prefix = ""
    if alert_rule == PRODUCTION_ALERT_RULE:
        emoji_prefix = "🚨 "
    severity = essentials.get("severity", "N/A")
    fired_date_time = format_alert_date(essentials.get("firedDateTime"))
    investigation_link = essentials.get("investigationLink", "#")

    alert_id_str = format_item("Alert ID", alert_id)
    severity_str = format_item("Severity", severity)
    date_str = format_item("Date", fired_date_time)

    message = (
        f"{emoji_prefix}*Azure Alert Fired: {alert_rule}*\n\n"
        f"{severity_str}\n"
        f"{date_str}\n"
        f"{alert_id_str}\n\n"
        f"---------------------------------------------------\n"
        f"{details}"
        f"<{investigation_link}|Click here to investigate in Azure Portal>"
    )

    return message


def send_to_slack(message: str) -> func.HttpResponse:
    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        logging.info(f"Successfully sent message to Slack. Status: {response.status_code}")
        return func.HttpResponse("Alert successfully forwarded to Slack.", status_code=200)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to Slack: {e}")
        return func.HttpResponse(f"Error sending to Slack: {e}", status_code=500)


@app.route(route="alert_to_slack", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def alert_to_slack(req: func.HttpRequest) -> func.HttpResponse:
    """
    Receives an alert from Azure Monitor, formats it, and sends it to Slack via webhook.
    """
    logging.info("alert_to_slack received a request.")

    provided_code = req.params.get("code")
    auth_response = validate_function_key(provided_code)
    if auth_response:
        return auth_response

    try:
        alert_payload = req.get_json()
    except ValueError:
        return func.HttpResponse("Request body is not valid JSON.", status_code=400)

    data = alert_payload.get("data", {})

    data_str = json.dumps(data, indent=2)  # pretty print 2 spaces indent
    if len(data_str) > 10000:  # 1 byte per char, roughly 10KB, Azure limits to 64KB
        data_str = data_str[:10000] + "... [truncated]"
    logging.info(f"Received Azure alert data:\n{data_str}")

    details = get_details_string(data)
    message = build_slack_message(data, details)
    slack_response = send_to_slack(message)

    return slack_response


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    A simple health check endpoint
    """
    logging.info("Health check endpoint was triggered.")
    return func.HttpResponse("Healthy.", status_code=200)
