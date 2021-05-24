
variable "account" {
  type                           = string
  description                    = "default aws account"
  default                        = "1234567890"
}

variable "ec2_keypair_name" {
  type                           = string
  description                    = "default ec2 keypair name"
  default                        = "keypair"
}

variable "my_ip_address" {
  type                           = string
  default                        = "192.168.0.1"
}

variable "region" {
  type                           = string
  description                    = "defualt aws region"
  default                        = "us-east-1"
}
