variable "location"          { type = string  default = "uksouth" }
variable "name_prefix"       { type = string  default = "inss" }
variable "env"               { type = string  default = "nonprod" }
variable "rg_name"           { type = string  default = null }
variable "aks_node_count"    { type = number  default = 2 }
variable "aks_node_size"     { type = string  default = "Standard_D4s_v5" }
variable "tags"              { type = map(string) default = { owner = "devops", costcentre = "platform" } }
