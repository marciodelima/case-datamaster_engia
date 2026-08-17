variable "location" {}
variable "resource_group_name" {}
variable "keyvault_name" {}
variable "db_password" {
  type      = string
  sensitive = true
}

