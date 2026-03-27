env "local" {
  src = "ent://ent/schema"
  dev = "docker://postgres/17/dev?search_path=public"
  migration {
    dir = "file://ent/migrate/migrations"
  }
}
