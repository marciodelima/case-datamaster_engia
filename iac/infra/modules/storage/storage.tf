resource "azurerm_storage_account" "storage" {
  name                     = var.nome_storage
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true

  identity {
    type         = "UserAssigned"
    identity_ids = [data.azurerm_user_assigned_identity.integration_identity.id]
  }

  blob_properties {
    last_access_time_enabled = true
    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}

resource "null_resource" "enable_last_access_tracking" {
  provisioner "local-exec" {
    command = "az storage account blob-service-properties update --account-name ${var.nome_storage} --resource-group ${var.resource_group_name} --enable-last-access-tracking true"
  }

  depends_on = [azurerm_storage_account.storage]
}


resource "azurerm_storage_container" "dados" {
  name                  = "dados"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"

  lifecycle {
    prevent_destroy = true
  }
  depends_on = [azurerm_storage_account.storage]
}

resource "azurerm_storage_management_policy" "policy" {
  storage_account_id = azurerm_storage_account.storage.id

  rule {
    name    = "delete_raw_after_7_days"
    enabled = true

    filters {
      prefix_match = ["dados/raw/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        delete_after_days_since_creation_greater_than = 7
      }
    }
  }

  rule {
    name    = "move_to_cool_after_7_days_no_access"
    enabled = true

    filters {
      prefix_match = ["dados/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        tier_to_cool_after_days_since_last_access_time_greater_than = 7
      }
    }
  }

  rule {
    name    = "move_to_cold_after_30_days_no_access"
    enabled = true

    filters {
      prefix_match = ["dados/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        tier_to_cold_after_days_since_last_access_time_greater_than = 30
      }
    }
  }
  depends_on = [null_resource.enable_last_access_tracking]
}

resource "azurerm_storage_data_lake_gen2_path" "folders" {
  count              = length(var.folders)
  path               = var.folders[count.index]
  filesystem_name    = azurerm_storage_container.dados.name
  storage_account_id = azurerm_storage_account.storage.id
  resource           = "directory"

  depends_on = [
    azurerm_storage_account.storage,
    azurerm_storage_container.dados,
    null_resource.enable_last_access_tracking
  ]
}

