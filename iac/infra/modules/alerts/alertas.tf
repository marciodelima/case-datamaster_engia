resource "azurerm_monitor_action_group" "alert_email_group" {
  name                = "alert-email-group"
  resource_group_name = var.resource_group_name
  short_name          = "emailGroup"

  email_receiver {
    name          = "adminEmail"
    email_address = var.email
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert" "job_failure_alert" {
  name                = "job-failure-alert"
  resource_group_name = var.resource_group_name
  location            = var.location
  description         = "Alerta para falhas de jobs no Databricks"
  severity            = 2
  enabled             = true
  frequency           = 5
  time_window         = 5

  data_source_id = var.workspace_logs_id

  query = <<QUERY
AzureDiagnostics
| where Category == "WorkspaceLogs"
| where OperationName == "JobRun"
| where RunState == "FAILED"
| summarize Falhas = count() by bin(TimeGenerated, 5m)
| where Falhas > 0
QUERY

  trigger {
    operator  = "GreaterThan"
    threshold = 0
  }

  action {
    action_group = [azurerm_monitor_action_group.alert_email_group.id]
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert" "job_duration_alert" {
  name                = "job-duration-alert"
  resource_group_name = var.resource_group_name
  location            = var.location
  description         = "Alerta para Jobs no Databricks com alto tempo de execução"
  severity            = 2
  enabled             = true
  frequency           = 5
  time_window         = 5
  data_source_id      = var.workspace_logs_id

  query = <<QUERY
AzureDiagnostics
| where Category == "WorkspaceLogs"
| where OperationName == "JobRun"
| where RunDuration > 3600
| summarize Longos = count() by bin(TimeGenerated, 5m)
| where Longos > 0
QUERY

  trigger {
    operator  = "GreaterThan"
    threshold = 0
  }

  action {
    action_group = [azurerm_monitor_action_group.alert_email_group.id]
  }
}

