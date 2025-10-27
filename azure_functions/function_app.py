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

    selected_columns = ["problemId", "outerMessage", "details", "client_City", "client_StateOrProvince", "cloud_RoleInstance"]
    selected_columns_indexes = {col: columns.index(col) for col in selected_columns}

    details = {}
    for row in rows:  # only one row expected but loop anyway
        entry = {col: row[selected_columns_indexes[col]] for col in selected_columns}
        details.update(entry)

    return details


def format_for_slack(data: dict) -> str:
    """
    Converts a dictionary into a formatted string with bolded keys for Slack messages.
    """
    if not data:
        return "_No additional details found._\n"
    formatted_lines = []
    for k, v in data.items():
        if k == "details":
            details = json.loads(v)
            if isinstance(details, list):
                for item in details:
                    for key, value in item.items():
                        if key == "rawStack" and isinstance(v, str):
                            # Format traceback as code block in Slack
                            stack = textwrap.dedent(value).strip()
                            formatted_lines.append(f"*{key}:*\n```{stack}```")
            else:
                formatted_lines.append(f"*details:* {details}")
        else:
            formatted_lines.append(f"*{k}:* {v}")
    formatted_message = "\n".join(formatted_lines) + "\n"
    return formatted_message


@app.route(route="alert_to_slack", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def alert_to_slack(req: func.HttpRequest) -> func.HttpResponse:
    """
    Receives an alert from Azure Monitor, formats it, and sends it to Slack via webhook.
    """
    logging.info("alert_to_slack processed a request.")

    provided_code = req.params.get("CODE")
    if not provided_code:
        return func.HttpResponse("Missing CODE authentication.", status_code=401)
    if provided_code != FUNCTION_KEY:
        logging.warning("Invalid CODE provided.")
        return func.HttpResponse("Unauthorized: invalid CODE.", status_code=403)

    try:
        alert_data = req.get_json()
    except ValueError:
        return func.HttpResponse("Request body is not valid JSON.", status_code=400)

    data = alert_data.get("data", {})

    data_str = json.dumps(data, indent=2)  # pretty print 2 spaces indent
    if len(data_str) > 10000:  # 1 byte per char, roughly 10KB, Azure limits to 64KB
        data_str = data_str[:10000] + "... [truncated]"
    logging.info(f"Received Azure alert data:\n{data_str}")

    # See https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-common-schema for available fields
    essentials = data.get("essentials", {})
    alert_id = essentials.get("alertId", "N/A")
    alert_rule = essentials.get("alertRule", "N/A")
    severity = essentials.get("severity", "N/A")
    fired_date_time = essentials.get("firedDateTime", "N/A")
    investigation_link = essentials.get("investigationLink", "#")

    alert_context = data.get("alertContext", {})
    condition = alert_context.get("condition", {})
    api_link = condition.get("allOf", [{}])[0].get("linkToSearchResultsAPI", "#")
    search_results = fetch_search_results(api_link)
    selected_search_results = select_search_results(search_results) if "error" not in search_results else {}
    details_str = format_for_slack(selected_search_results)

    message = (
        f"🚨 *Azure Alert Fired: {alert_rule}*\n\n"
        f"*Severity*: {severity}\n"
        f"*Date*: {fired_date_time}\n"
        f"*Alert ID*: {alert_id}\n\n"
        f"---------------------------------------------------\n"
        f"Details:\n"
        f"{details_str}"
        f"<{investigation_link}|Click here to investigate in Azure Portal>"
    )

    slack_payload = {"text": message}

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        logging.info(f"Successfully sent message to Slack. Status: {response.status_code}")
        return func.HttpResponse("Alert successfully forwarded to Slack.", status_code=200)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message to Slack: {e}")
        return func.HttpResponse(f"Error sending to Slack: {e}", status_code=500)


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    A simple health check endpoint
    """
    logging.info("Health check endpoint was triggered.")
    return func.HttpResponse("Healthy.", status_code=200)
