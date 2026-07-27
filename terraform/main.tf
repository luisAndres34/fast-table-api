# 1. Managed PostgreSQL Database Instance
resource "render_postgres" "postgres_db" {
  name          = "${var.app_name}-db"
  plan          = "free"
  region        = var.region
  database_name = var.db_name
  database_user = var.db_user
  version       = "15"
}

# 2. Managed Redis Instance
resource "render_redis" "redis_instance" {
  name              = "${var.app_name}-redis"
  plan              = "free"
  region            = var.region
  max_memory_policy = "allkeys_lru"
}

# 3. Main FastAPI Web Service (REST API)
resource "render_web_service" "api" {
  name          = var.app_name
  plan          = "free"
  region        = var.region
  start_command = "/app/start.sh"

  runtime_source = {
    native_runtime = {
      auto_deploy   = true
      branch        = "main"
      build_command = "uv sync --frozen"
      repo_url      = var.repo_url
      runtime       = "python"
    }
  }

  env_vars = {
    "PROJECT_NAME" = {
      value = var.app_name
    }
    "ENVIRONMENT" = {
      value = var.environment
    }
    "DATABASE_URL" = {
      value = "postgresql+asyncpg://${render_postgres.postgres_db.database_user}:${render_postgres.postgres_db.connection_info.password}@${render_postgres.postgres_db.connection_info.internal_connection_string}/${render_postgres.postgres_db.database_name}"
    }
    "REDIS_URL" = {
      value = render_redis.redis_instance.connection_info.internal_connection_string
    }
    "SECRET_KEY" = {
      value = var.secret_key
    }
    "STRIPE_SECRET_KEY" = {
      value = var.stripe_secret_key
    }
    "STRIPE_WEBHOOK_SECRET" = {
      value = var.stripe_webhook_secret
    }
    "SENTRY_DSN" = {
      value = var.sentry_dsn
    }
    "SENTRY_TRACES_SAMPLE_RATE" = {
      value = "1.0"
    }
  }
}

# 4. ARQ Async Worker (Background Job Processing)
resource "render_background_worker" "worker" {
  name          = "${var.app_name}-worker"
  plan          = "free"
  region        = var.region
  start_command = "uv run arq app.worker.WorkerSettings"

  runtime_source = {
    native_runtime = {
      auto_deploy   = true
      branch        = "main"
      build_command = "uv sync --frozen"
      repo_url      = var.repo_url
      runtime       = "python"
    }
  }

  env_vars = {
    "PROJECT_NAME" = {
      value = var.app_name
    }
    "ENVIRONMENT" = {
      value = var.environment
    }
    "DATABASE_URL" = {
      value = "postgresql+asyncpg://${render_postgres.postgres_db.database_user}:${render_postgres.postgres_db.connection_info.password}@${render_postgres.postgres_db.connection_info.internal_connection_string}/${render_postgres.postgres_db.database_name}"
    }
    "REDIS_URL" = {
      value = render_redis.redis_instance.connection_info.internal_connection_string
    }
    "SECRET_KEY" = {
      value = var.secret_key
    }
    "STRIPE_SECRET_KEY" = {
      value = var.stripe_secret_key
    }
    "STRIPE_WEBHOOK_SECRET" = {
      value = var.stripe_webhook_secret
    }
    "SENTRY_DSN" = {
      value = var.sentry_dsn
    }
  }
}
