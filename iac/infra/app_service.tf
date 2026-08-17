resource "azurerm_service_plan" "plan" {
  name                   = "appservice-plan"
  location               = var.location
  resource_group_name    = var.resource_group_name
  os_type                = "Linux"
  sku_name               = "S1"
  worker_count           = 1
  zone_balancing_enabled = false
}


#resource "azurerm_app_service" "frontend" {
#  name                = "frontend-investimentos-2025"
#  location            = var.location
#  resource_group_name = var.resource_group_name
#  app_service_plan_id = azurerm_service_plan.plan.id

#  site_config {
#    linux_fx_version = "NODE|18-lts"
#  }

#  app_settings = {
#    WEBSITE_RUN_FROM_PACKAGE = "1"
#  }
#}

#resource "azurerm_app_service" "backend" {
#  name                = "backend-investimentos-2025"
#  location            = var.location
#  resource_group_name = var.resource_group_name
#  app_service_plan_id = azurerm_service_plan.plan.id

#  site_config {
#    linux_fx_version = "PYTHON|3.11"
#  }

#  app_settings = {
#    WEBSITE_RUN_FROM_PACKAGE = "1"
#  }
#}

