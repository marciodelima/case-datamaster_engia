variable "location" {}
variable "resource_group_name" {}
variable "databricks_id" {}
variable "storage_id" {}
variable "eventhub_id" {}
variable "postgres_id" {}

variable "function_names" {
  type = list(string)
  default = [
    "news-producer-func1",
    "ri-resumer-func1",
    "ri-collector-func1",
    "finance-csv-ingestor-func1",
    "postgres-ingestor-func1",
    "news-sentiment-analyzer-func1"
  ]
}


