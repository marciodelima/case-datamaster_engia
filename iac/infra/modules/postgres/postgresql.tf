resource "azurerm_postgresql_flexible_server" "ri_db" {
  name                          = "finance-db-postgres-2025"
  resource_group_name           = var.resource_group_name
  location                      = var.location
  administrator_login           = "adminuser"
  administrator_password        = var.db_password
  version                       = "13"
  storage_mb                    = 32768
  sku_name                      = "B_Standard_B1ms"
  zone                          = "1"
  public_network_access_enabled = true
  auto_grow_enabled             = true

  authentication {
    active_directory_auth_enabled = true
  }

  tags = {
    environment = "production"
  }
}

resource "azurerm_postgresql_flexible_server_configuration" "enable_vector" {
  name       = "azure.extensions"
  server_id  = azurerm_postgresql_flexible_server.ri_db.id
  value      = "VECTOR"
  depends_on = [azurerm_postgresql_flexible_server.ri_db]
}

resource "azurerm_postgresql_flexible_server_database" "ri_db_main" {
  name       = "finance-db"
  server_id  = azurerm_postgresql_flexible_server.ri_db.id
  collation  = "en_US.utf8"
  charset    = "UTF8"
  depends_on = [azurerm_postgresql_flexible_server.ri_db]
}

resource "null_resource" "enable_pgvector" {
  provisioner "local-exec" {
    command = <<EOT
      PGPASSWORD=${var.db_password} psql \
        -h ${azurerm_postgresql_flexible_server.ri_db.fqdn} \
        -U adminuser \
        -d finance-db \
        -c "CREATE EXTENSION IF NOT EXISTS vector;"
    EOT
  }
  depends_on = [
    azurerm_postgresql_flexible_server_database.ri_db_main,
    azurerm_postgresql_flexible_server_configuration.enable_vector
  ]
}

data "external" "github_runner_ip" {
  program = ["bash", "-c", "echo '{\"ip\": \"'$(curl -s https://ifconfig.me)'\"}'"]
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "github_actions_ip" {
  name             = "AllowGitHubActions"
  server_id        = azurerm_postgresql_flexible_server.ri_db.id
  start_ip_address = data.external.github_runner_ip.result.ip
  end_ip_address   = data.external.github_runner_ip.result.ip
}

resource "null_resource" "init_sql" {
  depends_on = [azurerm_postgresql_flexible_server.ri_db, azurerm_postgresql_flexible_server_database.ri_db_main]

  provisioner "local-exec" {
    command = <<EOT
      sleep 60
      echo "Executando init.sql no PostgreSQL..."
      PGPASSWORD=${var.db_password} psql \
        -h ${azurerm_postgresql_flexible_server.ri_db.fqdn} \
        -U adminuser \
        -d finance-db \
        -f ${path.module}/init.sql \
        --set ON_ERROR_STOP=off
    EOT
  }
  triggers = {
    always_run = timestamp()
  }
}

data "azurerm_key_vault" "main" {
  name                = var.keyvault_name
  resource_group_name = var.resource_group_name
}

resource "azurerm_key_vault_secret" "postgres_conn_string" {
  name         = "Postgres-Conn"
  key_vault_id = data.azurerm_key_vault.main.id

  value = "Host=${azurerm_postgresql_flexible_server.ri_db.fqdn};Port=5432;Database=${azurerm_postgresql_flexible_server_database.ri_db_main.name};User Id=${azurerm_postgresql_flexible_server.ri_db.administrator_login};Password=${var.db_password};Ssl Mode=Require"

  depends_on = [azurerm_postgresql_flexible_server.ri_db, azurerm_postgresql_flexible_server_database.ri_db_main]
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure_services" {
  name                = "AllowAzureServices"
  server_id           = azurerm_postgresql_flexible_server.ri_db.id
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
  depends_on          = [azurerm_postgresql_flexible_server.ri_db]
}

