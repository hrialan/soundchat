resource "google_cloudbuild_trigger" "soundchat-deploy" {
  github {
    owner = "hrialan"
    name  = local.app_name

    push {
      branch = "main"
    }
  }

  substitutions = {
    _LOCATION                     = local.region
    _ARTIFACT_REGISTRY_REPOSITORY = local.artifactregistry_repository
    _ARTIFACT_REGISTRY_IMAGE      = local.app_name
  }
  name            = "${local.app_name}-deploy"
  filename        = "cloudbuild.yaml"
  service_account = google_service_account.deploy.id
}
