from aws_gdpr_guard.obfuscator import obfuscate_file


def test_obfuscate_file():
    file_to_obfuscate = ""
    pii_fields = ""
    expected = None
    result = obfuscate_file(file_to_obfuscate, pii_fields)
    assert result == expected
