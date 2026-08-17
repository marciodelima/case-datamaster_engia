variable "location" { default = "brazilsouth" }
variable "resource_group_name" { default = "rsg-datamaster" }
variable "spn_name" { default = "github-deploy-spn" }
variable "keyvault_name" { default = "kv-secret-datamastermdl3" }
variable "keyvault_rg" { default = "rsg-datamaster" }
variable "name_databricks" { default = "finance-databricks" }
variable "iac_terraform_storage" { default = "tfstatedatamastersta3" }
variable "brapi-dev-apikey" { default = "vT3QiPMg67zdiyeM9Dxgj7" }

variable "databricks_resource" {
  default = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"
}

variable "admin_email" { default = "marcio.lima.f1rst.2025.10@gmail.com" }

variable "tags" {
  description = "Tags padrão"
  type        = map(string)
  default = {
    environment = "production"
    owner       = "marcio"
  }
}




