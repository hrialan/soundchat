resource "google_firestore_database" "app-db" {
  name        = "${local.app_name}-firestore-db"
  location_id = local.region
  type        = "FIRESTORE_NATIVE"
}
