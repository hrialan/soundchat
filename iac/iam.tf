resource "google_service_account" "deploy" {
  account_id   = "${local.app_name}-deploy"
  display_name = "Deploy Service Account for ${local.app_name}"
}

resource "google_project_iam_member" "deploy-run-admin" {
  for_each = toset(local.deploy_roles)
  project  = data.google_project.project.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.deploy.email}"
}


resource "google_service_account" "cloud-run" {
  account_id   = "${local.app_name}-cloud-run"
  display_name = "Cloud Run Service Account for ${local.app_name}"
}

resource "google_secret_manager_secret_iam_member" "cloud-run-secret-access-spotify-client-id" {
  secret_id = google_secret_manager_secret.spotify-client-id.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud-run.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud-run-secret-access-spotify-client-secret" {
  secret_id = google_secret_manager_secret.spotify-client-secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud-run.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud-run-secret-access-encryption-key" {
  secret_id = google_secret_manager_secret.encryption-key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud-run.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud-run-secret-access-openai-api-key" {
  secret_id = google_secret_manager_secret.openai-api-key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud-run.email}"
}

resource "google_project_iam_member" "cloud-run-firestore-user" {
  project = data.google_project.project.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud-run.email}"
}
