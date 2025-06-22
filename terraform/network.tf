locals {
  private_endpoint_prefix           = lower("pe-cdt-pub-vip-ddrc-${local.env_letter}")
  private_service_connection_prefix = lower("psc-cdt-pub-vip-ddrc-${local.env_letter}")
}
