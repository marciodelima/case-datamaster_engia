resource "azurerm_resource_group" "rsg_datamaster" {
  name     = var.resource_group_name
  location = var.location
  tags = {
    projeto    = "DataMaster"
    ambiente   = "producao"
    criado_por = "marcio"
  }
}
