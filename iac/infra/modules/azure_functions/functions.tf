resource "azurerm_service_plan" "func_plan" {
  name                = "func-plan"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = "S1"
  worker_count        = 2
}

resource "azurerm_application_insights" "finance_logs_news" {
  name                = "finance-appins-logs-news"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
}

resource "azurerm_application_insights" "finance_logs_csv" {
  name                = "finance-appins-logs-csv"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
}

resource "azurerm_application_insights" "finance_logs_ri" {
  name                = "finance-appins-logs-ri"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
}

resource "azurerm_application_insights" "finance_logs_ri_collector" {
  name                = "finance-appins-logs-ri-collector"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
}

resource "azurerm_application_insights" "finance_logs_postgres" {
  name                = "finance-appins-logs-postgres"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
}

resource "azurerm_application_insights" "finance_logs_sentiment" {
  name                = "finance-appins-logs-sentiment"
  location            = var.location
  resource_group_name = var.resource_group_name
  application_type    = "web"
}

resource "azurerm_linux_function_app" "news_producer" {
  name                       = "news-producer-func1"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.news_storage.name
  storage_account_access_key = azurerm_storage_account.news_storage.primary_access_key

  site_config {
    always_on = true
    application_stack {
      python_version = "3.10"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME         = "python"
    WEBSITE_RUN_FROM_PACKAGE         = "1"
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"
    WEBSITE_HEALTHCHECK_MAXPINGFAILURES = "1"
    APPINSIGHTS_INSTRUMENTATIONKEY   = azurerm_application_insights.finance_logs_news.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.finance_logs_news.connection_string
    EVENTHUB_NAME      = var.eventhub_topic
    EVENTHUB_NAMESPACE = "${var.eventhub_namespace_name}.servicebus.windows.net"
    KEYVAULT_URI = "https://${var.keyvault_name}.vault.azure.net"
  }
}

resource "azurerm_linux_function_app" "finance_csv_ingestor" {
  name                       = "finance-csv-ingestor-func1"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.finance_storage.name
  storage_account_access_key = azurerm_storage_account.finance_storage.primary_access_key

  site_config {
    always_on = true
    application_stack {
      python_version = "3.10"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME         = "python"
    WEBSITE_RUN_FROM_PACKAGE         = "1"
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"
    WEBSITE_HEALTHCHECK_MAXPINGFAILURES = "1"
    APPINSIGHTS_INSTRUMENTATIONKEY   = azurerm_application_insights.finance_logs_csv.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.finance_logs_csv.connection_string
    KEYVAULT_URI = "https://${var.keyvault_name}.vault.azure.net"
    STORAGE_URL  = "https://${var.existing_storage_account_name}.blob.core.windows.net"
  }
}

resource "azurerm_linux_function_app" "ri_resumer" {
  name                       = "ri-resumer-func1"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.ri_storage.name
  storage_account_access_key = azurerm_storage_account.ri_storage.primary_access_key

  site_config {
    always_on = true
    application_stack {
      python_version = "3.10"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME         = "python"
    WEBSITE_RUN_FROM_PACKAGE         = "1"
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"
    WEBSITE_HEALTHCHECK_MAXPINGFAILURES = "1"
    APPINSIGHTS_INSTRUMENTATIONKEY   = azurerm_application_insights.finance_logs_ri.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.finance_logs_ri.connection_string
    KEYVAULT_URI = "https://${var.keyvault_name}.vault.azure.net"
    STORAGE_URL  = "https://${var.existing_storage_account_name}.blob.core.windows.net"
    DELTA_PATH   = "abfss://dados@${var.existing_storage_account_name}.blob.core.windows.net/bronze/resultado_ri"
  }
}

resource "azurerm_linux_function_app" "ri_collector" {
  name                       = "ri-collector-func1"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.ri_collector_storage.name
  storage_account_access_key = azurerm_storage_account.ri_collector_storage.primary_access_key

  site_config {
    always_on = true
    application_stack {
      python_version = "3.10"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME         = "python"
    WEBSITE_RUN_FROM_PACKAGE         = "1"
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"
    WEBSITE_HEALTHCHECK_MAXPINGFAILURES = "1"
    APPINSIGHTS_INSTRUMENTATIONKEY   = azurerm_application_insights.finance_logs_ri_collector.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.finance_logs_ri_collector.connection_string
    KEYVAULT_URI = "https://${var.keyvault_name}.vault.azure.net"
    STORAGE_URL  = "https://${var.existing_storage_account_name}.blob.core.windows.net"
    DELTA_PATH  = "abfss://dados@${var.existing_storage_account_name}.blob.core.windows.net/raw/ri"
  }
}

resource "azurerm_linux_function_app" "postgres_ingestor" {
  name                       = "postgres-ingestor-func1"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.postgres_storage.name
  storage_account_access_key = azurerm_storage_account.postgres_storage.primary_access_key

  site_config {
    always_on = true
    application_stack {
      python_version = "3.10"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME         = "python"
    WEBSITE_RUN_FROM_PACKAGE         = "1"
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"
    WEBSITE_HEALTHCHECK_MAXPINGFAILURES = "1"
    APPINSIGHTS_INSTRUMENTATIONKEY   = azurerm_application_insights.finance_logs_postgres.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.finance_logs_postgres.connection_string
    KEYVAULT_URI = "https://${var.keyvault_name}.vault.azure.net"
    STORAGE_URL  = "https://${var.existing_storage_account_name}.blob.core.windows.net"
    DELTA_PATH  = "abfss://dados@${var.existing_storage_account_name}.blob.core.windows.net/bronze"
  }
}

resource "azurerm_linux_function_app" "news_sentiment_analyzer" {
  name                       = "news-sentiment-analyzer-func1"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.func_plan.id
  storage_account_name       = azurerm_storage_account.sentiment_storage.name
  storage_account_access_key = azurerm_storage_account.sentiment_storage.primary_access_key

  site_config {
    always_on = true
    application_stack {
      python_version = "3.10"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME         = "python"
    WEBSITE_RUN_FROM_PACKAGE         = "1"
    PYTHON_ENABLE_WORKER_EXTENSIONS = "1"
    WEBSITE_HEALTHCHECK_MAXPINGFAILURES = "1"
    APPINSIGHTS_INSTRUMENTATIONKEY   = azurerm_application_insights.finance_logs_sentiment.instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.finance_logs_sentiment.connection_string
    EVENTHUB_NAME      = var.eventhub_topic
    EVENTHUB_NAMESPACE = "${var.eventhub_namespace_name}.servicebus.windows.net"
    EVENTHUB_CONNECTION = "@Microsoft.KeyVault(SecretUri=https://${var.keyvault_name}.vault.azure.net/secrets/EventHubConnectionString/)"
    KEYVAULT_URI = "https://${var.keyvault_name}.vault.azure.net"
    STORAGE_URL = "https://${var.existing_storage_account_name}.blob.core.windows.net"
    DELTA_PATH  = "abfss://dados@${var.existing_storage_account_name}.blob.core.windows.net/bronze"
  }
}


