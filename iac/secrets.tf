resource "google_secret_manager_secret" "spotify-client-id" {
  secret_id = "${local.app_name}-spotify-client-id"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "spotify-client-secret" {
  secret_id = "${local.app_name}-spotify-client-secret"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "encryption-key" {
  secret_id = "${local.app_name}-encryption-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "openai-api-key" {
  secret_id = "${local.app_name}-openai-api-key"

  replication {
    auto {}
  }
}
