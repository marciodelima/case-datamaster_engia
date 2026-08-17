data "azurerm_function_app" "functions" {
  for_each            = toset(var.function_names)
  name                = each.key
  resource_group_name = var.resource_group_name
}

locals {
  function_ids = {
    for name in var.function_names :
    name => try(data.azurerm_function_app.functions[name].id, null)
  }

  finance_dashboard_json = jsonencode({
    lenses = {
      "0" = {
        order = 0
        parts = merge({
          "0" = {
            position = { x = 0, y = 0, rowSpan = 2, colSpan = 12 }
            metadata = {
              type = "Extension/HubsExtension/PartType/MarkdownPart"
              settings = {
                content = "# Observabilidade Financeira\n\nInfraestrutura • Dados • Banco • Funções"
              }
            }
          }
          "1" = {
            position = { x = 0, y = 2, rowSpan = 6, colSpan = 6 }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = var.databricks_id }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "line"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.Databricks/workspaces"
                      metricName      = "ClusterCount"
                      aggregation     = "Average"
                    }
                  ]
                }
              }
            }
          }
          "2" = {
            position = { x = 6, y = 2, rowSpan = 6, colSpan = 6 }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = var.databricks_id }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "column"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.Databricks/workspaces"
                      metricName      = "JobSuccessCount"
                      aggregation     = "Total"
                    },
                    {
                      metricNamespace = "Microsoft.Databricks/workspaces"
                      metricName      = "JobFailureCount"
                      aggregation     = "Total"
                    }
                  ]
                }
              }
            }
          }
          "3" = {
            position = { x = 0, y = 8, rowSpan = 6, colSpan = 6 }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = var.storage_id }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "area"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.Storage/storageAccounts"
                      metricName      = "UsedCapacity"
                      aggregation     = "Average"
                    },
                    {
                      metricNamespace = "Microsoft.Storage/storageAccounts"
                      metricName      = "Transactions"
                      aggregation     = "Total"
                    }
                  ]
                }
              }
            }
          }
          "4" = {
            position = { x = 6, y = 8, rowSpan = 6, colSpan = 6 }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = var.eventhub_id }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "column"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.EventHub/namespaces"
                      metricName      = "IncomingMessages"
                      aggregation     = "Total"
                    },
                    {
                      metricNamespace = "Microsoft.EventHub/namespaces"
                      metricName      = "OutgoingMessages"
                      aggregation     = "Total"
                    }
                  ]
                }
              }
            }
          }
          "5" = {
            position = { x = 0, y = 14, rowSpan = 6, colSpan = 6 }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = var.postgres_id }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "line"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.DBforPostgreSQL/flexibleServers"
                      metricName      = "cpu_percent"
                      aggregation     = "Average"
                    },
                    {
                      metricNamespace = "Microsoft.DBforPostgreSQL/flexibleServers"
                      metricName      = "memory_percent"
                      aggregation     = "Average"
                    }
                  ]
                }
              }
            }
          }
        },
        {
          for idx, name in var.function_names :
          tostring(100 + idx) => {
            position = {
              x       = idx % 2 == 0 ? 0 : 6
              y       = 20 + floor(idx / 2) * 6
              rowSpan = 6
              colSpan = 6
            }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = local.function_ids[name] }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "column"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.Web/sites"
                      metricName      = "FunctionExecutionCount"
                      aggregation     = "Total"
                    },
                    {
                      metricNamespace = "Microsoft.Web/sites"
                      metricName      = "Http5xx"
                      aggregation     = "Total"
                    }
                  ]
                }
              }
            }
          } if local.function_ids[name] != null
        })
      }
    }
    metadata = {
      model = {
        timeRange = {
          value = {
            relative = {
              duration = 24
              timeUnit = 1
            }
          }
        }
      }
    }
  })

  jobs_dashboard_json = jsonencode({
    lenses = {
      "0" = {
        order = 0
        parts = {
          "0" = {
            position = { x = 0, y = 0, rowSpan = 2, colSpan = 12 }
            metadata = {
              type = "Extension/HubsExtension/PartType/MarkdownPart"
              settings = {
                content = "# Execução de Jobs Databricks"
              }
            }
          }
          "1" = {
            position = { x = 0, y = 2, rowSpan = 6, colSpan = 6 }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = var.databricks_id }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "column"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.Databricks/workspaces"
                      metricName      = "JobSuccessCount"
                      aggregation     = "Total"
                    },
                    {
                      metricNamespace = "Microsoft.Databricks/workspaces"
                      metricName      = "JobFailureCount"
                      aggregation     = "Total"
                    }
                  ]
                }
              }
            }
          }
          "2" = {
            position = { x = 6, y = 2, rowSpan = 6, colSpan = 6 }
            metadata = {
              type   = "Extension/MetricsExplorerPart"
              inputs = { scope = var.databricks_id }
              settings = {
                content = {
                  version   = "1.0"
                  chartType = "line"
                  metrics = [
                    {
                      metricNamespace = "Microsoft.Databricks/workspaces"
                      metricName      = "JobRunTime"
                      aggregation     = "Average"
                    }
                  ]
                }
              }
            }
          }
        }
      }
    }
    metadata = {
      model = {
        timeRange = {
          value = {
            relative = {
              duration = 24
              timeUnit = 1
            }
          }
        }
      }
    }
  })
}

resource "azurerm_portal_dashboard" "finance_dashboard" {
  name                  = "finance-observability"
  resource_group_name   = var.resource_group_name
  location              = var.location
  tags                  = { dash = "geral" }
  dashboard_properties  = local.finance_dashboard_json
}

resource "azurerm_portal_dashboard" "jobs_dashboard" {
  name                  = "jobs-execution-dashboard"
  resource_group_name   = var.resource_group_name
  location              = var.location
  tags                  = { dash = "jobs databricks" }
  dashboard_properties  = local.jobs_dashboard_json
}

