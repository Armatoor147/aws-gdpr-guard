# # ZIP File (of the library)
# data "archive_file" "aws_gdpr_guard-library" {
#     type        = "zip"
#     source_dir  = "${path.module}/../../aws_gdpr_guard"
#     output_path = "${path.module}/aws_gdpr_guard.zip"
# }