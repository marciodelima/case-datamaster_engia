resource "random_id" "suffix" {
  byte_length = 4
}

resource "azurerm_storage_account" "news_storage" {
  name                     = "newsfuncstorage${random_id.suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account" "finance_storage" {
  name                     = "finfuncstorage${random_id.suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account" "ri_storage" {
  name                     = "rifuncstorage${random_id.suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account" "ri_collector_storage" {
  name                     = "ricollectstorage${random_id.suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account" "postgres_storage" {
  name                     = "dbfuncstorage${random_id.suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_account" "sentiment_storage" {
  name                     = "sentfuncstorage${random_id.suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "news_code" {
  name                  = "function-code-news"
  storage_account_id    = azurerm_storage_account.news_storage.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "finance_code" {
  name                  = "function-code-finance"
  storage_account_id    = azurerm_storage_account.finance_storage.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "ri_code" {
  name                  = "function-code-ri"
  storage_account_id  = azurerm_storage_account.ri_storage.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "ri_collector_code" {
  name                  = "function-code-ri-collector"
  storage_account_id  = azurerm_storage_account.ri_collector_storage.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "postgres_code" {
  name                  = "function-code-postgres"
  storage_account_id  = azurerm_storage_account.postgres_storage.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "sentiment_code" {
  name                  = "function-code-sentiment"
  storage_account_id  = azurerm_storage_account.sentiment_storage.id
  container_access_type = "private"
}

