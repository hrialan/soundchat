terraform {
  required_version = "~> 1.9.5"
  backend "gcs" {
    bucket = "dgc-sandbox-hrialan-terraform"
    prefix = "soundchat-init/"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.3.0"
    }
  }
}

provider "google" {
  project = "sandbox-hrialan"
}

provider "google-beta" {
  project = "sandbox-hrialan"
}
data "google_project" "project" {
}
