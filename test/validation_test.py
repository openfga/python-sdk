import unittest

from openfga_sdk.validation import is_well_formed_ulid_string


class TestValidation(unittest.TestCase):
    """Test for validation"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_well_formed_ulid_string_valid_ulids(self):
        self.assertEqual(
            is_well_formed_ulid_string("01H0GVCS1HCQM6SJRJ4A026FZ9"),
            True,
            "Should be True",
        )
        self.assertEqual(
            is_well_formed_ulid_string("01H0GVD9ACPFKGMWJV0Y93ZM7H"),
            True,
            "Should be True",
        )
        self.assertEqual(
            is_well_formed_ulid_string("01H0GVDH0FRZ4WAFED6T9KZYZR"),
            True,
            "Should be True",
        )
        self.assertEqual(
            is_well_formed_ulid_string("01H0GVDSW72AZ8QV3R0HJ91QBX"),
            True,
            "Should be True",
        )

    def test_is_well_formed_ulid_string_invalid_ulids(self):
        self.assertEqual(is_well_formed_ulid_string("abc"), False, "Should be False")
        self.assertEqual(is_well_formed_ulid_string(123), False, "Should be False")
        self.assertEqual(is_well_formed_ulid_string(None), False, "Should be False")
        self.assertEqual(
            is_well_formed_ulid_string("01H0GVDSW72AZ8QV3R0HJ91QBXa"),
            False,
            "Should be False",
        )
        self.assertEqual(
            is_well_formed_ulid_string("b523ad13-8adb-4803-a6db-013ac50197ca"),
            False,
            "Should be False",
        )
        self.assertEqual(
            is_well_formed_ulid_string("9240BFC0-DA00-457B-A328-FC370A598D60"),
            False,
            "Should be False",
        )
