import unittest
from pathlib import Path
from backend.app.credentials import validate_credential


class CredentialTests(unittest.TestCase):
    def test_example_credentials_are_rejected(self):
        for line in (Path(__file__).resolve().parents[2] / '.env.example').read_text().splitlines():
            name, _, value = line.partition('=')
            if name in ('SECRET_KEY', 'ADMIN_PASSWORD'):
                with self.subTest(name=name), self.assertRaises(RuntimeError):
                    validate_credential(value, name)

    def test_weak_values_are_rejected(self):
        for name in ('SECRET_KEY', 'ADMIN_PASSWORD'):
            for value in ('', 'admin123', 'mouse-secret-key-2026', 'ab' * 30, 'replace_with_a_very_long_secret_123456789'):
                with self.subTest(name=name, value=value), self.assertRaises(RuntimeError):
                    validate_credential(value, name)

    def test_valid_values_are_preserved(self):
        for name, value in [('SECRET_KEY', 'abcDEF0123456789!mnoPQRstUVWxyz4567'), ('ADMIN_PASSWORD', 'Initial-Test-Pw-2026')]:
            self.assertEqual(validate_credential(value, name), value)
