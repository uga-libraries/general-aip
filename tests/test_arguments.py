"""Testing for the function check_arguments, which tests the correctness of input from sys.argv and
 returns variable values and error messages, if any."""

import unittest
from scripts.aip_functions import check_arguments


class TestCheckArguments(unittest.TestCase):

    def test_one_arg(self):
        """
        Test for if the user supplies no arguments. There is still one argument in sys.argv, the script name.
        """
        result = check_arguments(['general-aip.py'])
        expected = (None, True, None, ['AIPs directory argument is missing.', 'Cannot check for the metadata.csv in the AIPs directory because the AIPs directory has an error.'])
        self.assertEqual(result, expected, 'Problem with error handling for one argument')

if __name__ == '__main__':
    unittest.main()