variable "render_api_key" {
  description = "API Key from Render Cloud account"
  type        = string
  sensitive   = true
}

variable "render_owner_id" {
  description = "Render Owner or Team ID (usr-xxx or team-xxx)"
  type        = string
}

variable "region" {
  description = "Render Cloud deployment region (oregon, frankfurt, singapore, ohio)"
  type        = string
  default     = "oregon"
}

variable "environment" {
  description = "Deployment environment (production, staging)"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Name prefix for services"
  type        = string
  default     = "fast-table-api"
}

variable "db_name" {
  description = "PostgreSQL Database Name"
  type        = string
  default     = "api_db"
}

variable "db_user" {
  description = "PostgreSQL Master Username"
  type        = string
  default     = "postgres"
}

variable "secret_key" {
  description = "JWT Signing Secret Key for FastAPI"
  type        = string
  sensitive   = true
}

variable "stripe_secret_key" {
  description = "Stripe API Secret Key"
  type        = string
  sensitive   = true
  default     = "sk_test_mock_key"
}

variable "stripe_webhook_secret" {
  description = "Stripe Webhook Signing Secret"
  type        = string
  sensitive   = true
  default     = "whsec_mock_secret"
}

variable "sentry_dsn" {
  description = "Sentry Error Tracking DSN URL"
  type        = string
  default     = ""
}

variable "repo_url" {
  description = "GitHub Repository URL for deployment"
  type        = string
  default     = "https://github.com/luisAndres34/fast-table-api"
}
