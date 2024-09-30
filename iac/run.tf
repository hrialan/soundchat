resource "google_cloud_run_v2_service" "soundchat" {
  provider = google-beta
  name     = local.app_name
  location = local.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    max_instance_request_concurrency = 80
    service_account                  = google_service_account.cloud-run.email
    annotations = {
      "launchStage"        = "BETA"
      "force-new-revision" = timestamp()
    }
    containers {
      image = "${local.region}-docker.pkg.dev/${data.google_project.project.project_id}/${local.artifactregistry_repository}/${local.app_name}:latest"

      # volume_mounts {
      #   mount_path = "/mnt/${local.app_name}-app-memory-storage"
      #   name       = "${local.app_name}-app-memory-storage"
      # }

      env {
        name = "SPOTIPY_CLIENT_ID"
        value_source {
          secret_key_ref {
            version = "latest"
            secret  = google_secret_manager_secret.spotify-client-id.secret_id
          }
        }
      }
      env {
        name = "SPOTIPY_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            version = "latest"
            secret  = google_secret_manager_secret.spotify-client-secret.secret_id
          }
        }
      }
      env {
        name  = "SPOTIPY_REDIRECT_URI"
        value = local.spotify_redirect_uri
      }
      env {
        name  = "FLASK_SESSION_DIR"
        value = "/.flask_session"
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = data.google_project.project.project_id
      }
      env {
        name  = "FIRESTORE_DATABASE"
        value = google_firestore_database.app-db.name
      }
      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            version = "latest"
            secret  = google_secret_manager_secret.openai-api-key.secret_id
          }
        }
      }
      env {
        name = "ENCRYPTION_KEY"
        value_source {
          secret_key_ref {
            version = "latest"
            secret  = google_secret_manager_secret.encryption-key.secret_id
          }
        }
      }
      ports {
        container_port = 8080
      }
      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }
    }
    # volumes {
    #   name = "${local.app_name}-app-memory-storage"
    #   empty_dir {
    #     medium     = "MEMORY"
    #     size_limit = "1Gi"
    #   }
    # }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
}
