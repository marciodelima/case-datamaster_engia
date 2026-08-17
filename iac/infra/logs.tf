resource "azurerm_log_analytics_workspace" "logs" {
  name                = "finance-logs"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_monitor_diagnostic_setting" "dbx_diag" {
  name                       = "dbx-diagnostics"
  target_resource_id         = module.databricks.workspace_id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id

  enabled_log {
    category = "Jobs"
  }

}

resource "azurerm_monitor_diagnostic_setting" "storage_diag" {
  name                       = "storage-diagnostics"
  target_resource_id         = module.storage.storage_id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id

  enabled_metric {
    category = "Transaction"
  }

  enabled_metric {
    category = "Capacity"
  }

}

resource "azurerm_monitor_diagnostic_setting" "eventhub_diag" {
  name                       = "eventhub-diagnostics"
  target_resource_id         = module.event_hubs.eventhub_namespace_id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id

  enabled_log {
    category = "OperationalLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

resource "azurerm_monitor_diagnostic_setting" "postgres_diag" {
  name                       = "diag-postgres"
  target_resource_id         = module.postgres.server_id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id

  enabled_log {
    category = "PostgreSQLLogs"
  }

  enabled_metric {
    category = "AllMetrics"
  }
}

