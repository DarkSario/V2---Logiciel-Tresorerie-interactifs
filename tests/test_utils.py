import unittest
from utils.validation import is_email, is_number, is_integer, is_required

class TestValidation(unittest.TestCase):
    def test_is_email(self):
        self.assertTrue(is_email("test@ex.com"))
        self.assertFalse(is_email("toto"))
        self.assertFalse(is_email("a@b"))
    def test_is_number(self):
        self.assertTrue(is_number("3.14"))
        self.assertTrue(is_number("12"))
        self.assertFalse(is_number("abc"))
    def test_is_integer(self):
        self.assertTrue(is_integer("10"))
        self.assertTrue(is_integer(5))
        self.assertFalse(is_integer("5.7"))
    def test_is_required(self):
        self.assertTrue(is_required("a"))
        self.assertFalse(is_required(""))
        self.assertFalse(is_required(None))

if __name__ == "__main__":
    unittest.main()