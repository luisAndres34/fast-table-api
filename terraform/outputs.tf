output "api_web_service_url" {
  description = "Public URL of the FastAPI Web Service on Render"
  value       = render_web_service.api.url
}

output "swagger_docs_url" {
  description = "URL to access Swagger UI OpenAPI Documentation"
  value       = "${render_web_service.api.url}/docs"
}

output "postgres_database_name" {
  description = "Name of the managed PostgreSQL database"
  value       = render_postgres.postgres_db.database_name
}

output "redis_connection_string" {
  description = "Internal connection string for Redis"
  value       = render_redis.redis_instance.connection_info.internal_connection_string
  sensitive   = true
}
