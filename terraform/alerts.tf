locals {
  app_error_subject = local.is_prod ? "🚨 Application Error" : "${local.env_name}: Application Error"
  app_error_name    = "msqalert-cdt-pub-vip-ddrc-${local.env_letter}-001"
}

resource "azurerm_monitor_scheduled_query_rules_alert_v2" "app_error" {
  name                = local.app_error_name
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  scopes              = [module.monitoring.application_insights_id]

  description  = "Alerts when any exception is logged in Application Insights."
  display_name = local.app_error_name
  enabled      = true
  severity     = 2

  # 5 minutes, in ISO 8601 duration format
  evaluation_frequency = "PT5M"
  window_duration      = "PT5M"

  criteria {
    query     = <<-QUERY
      union exceptions, (traces | where severityLevel >= 3)
    QUERY
    operator  = "GreaterThan"
    threshold = 0
    time_aggregation_method = "Count"

    failing_periods {
      minimum_failing_periods_to_trigger_alert = 1
      number_of_evaluation_periods             = 1
    }
  }

  action {
    action_groups = [module.monitoring.action_group_id]
    custom_properties = {
      subject = local.app_error_subject
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
