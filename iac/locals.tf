locals {
  app_name = "soundchat"
  region   = "europe-west9"

  artifactregistry_repository = "cloud-run-source-deploy"
  spotify_redirect_uri        = "https://${local.app_name}-${data.google_project.project.number}.${local.region}.run.app"

  deploy_roles = [
    "roles/run.admin",
    "roles/artifactregistry.writer",
    "roles/logging.logWriter",
    "roles/storage.admin",
    "roles/secretmanager.admin",
    "roles/iam.serviceAccountAdmin",
    "roles/cloudbuild.builds.builder",
    "roles/iam.serviceAccountAdmin",
    "roles/iam.serviceAccountUser",
    "roles/resourcemanager.projectIamAdmin",
    "roles/datastore.owner",
  ]
}
