output "ecs_cluster_name" {
  value = aws_ecs_cluster.aws_gdpr_guard_cluster.name
}

# output "ecs_service_name" {
#   value = aws_ecs_service.gdpr_guard_service.name
# }