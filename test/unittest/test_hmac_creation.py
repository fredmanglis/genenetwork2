import unittest

from wqflask.user_manager import actual_hmac_creation

class TestHmacCreation(unittest.TestCase):

    def testHmacCreation(self):
        secret = "SOME_SECRET_0123456_ABCDEF"
        data = "SOME_STRING"
        expected_hmac = "0791a3dcc317d22fdc06"
        actual_hmac = actual_hmac_creation(data, secret)
        self.assertEqual(
            actual_hmac
            , expected_hmac
            , "Expected `%s` but got `%s`" % (expected_hmac, actual_hmac))


if __name__ == "__main__":
    unittest.main()
