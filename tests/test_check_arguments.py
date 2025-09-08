"""Testing for the function check_arguments, which tests the correctness of user input from sys.argv and
 returns a list with the variable values and error messages, if any."""

import os
import unittest
from aip_functions import check_arguments


class TestCheckArguments(unittest.TestCase):

    def test_metadata_missing(self):
        """Test for when the arguments are correct but the metadata.csv is not in the expected location"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'no_metadata_csv')
        result = check_arguments(['general-aip.py', aips_dir, 'general', 'zip'])
        errors = ['Missing the required file metadata.csv in the AIPs directory.']
        expected = (aips_dir, 'general', True, None, None, errors)
        self.assertEqual(expected, result, "Problem with test for metadata_missing")

    def test_no_argument(self):
        """
        Test for if the user supplies no arguments.
        There is still one value in sys.argv, the script name.
        """
        result = check_arguments(['general-aip.py'])
        errors = ['AIPs directory argument is missing.',
                  'Cannot check for the metadata.csv because the AIPs directory has an error.']
        expected = (None, None, None, None, None, errors)
        self.assertEqual(expected, result, "Problem with test for no argument provided")

    def test_to_zip_argument_error(self):
        """
        Test for if to_zip is not one of the expected values.
        """
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'general', 'error'])
        errors = ['To zip is not an expected value.']
        expected = (aips_dir, 'general', None, None, os.path.join(aips_dir, 'metadata.csv'), errors)
        self.assertEqual(expected, result, "Problem with test for to_zip argument error")

    def test_required_argument(self):
        """
        Test for if the aips_directory (first required argument) is present and the path is valid.
        """
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'general', 'zip'])
        expected = (aips_dir, 'general', True, None, os.path.join(aips_dir, 'metadata.csv'), [])
        self.assertEqual(expected, result, "Problem with test for required argument only, correct")

    def test_required_argument_error(self):
        """
        Test for if the aips_directory (required argument) is present but the path is not valid.
        """
        result = check_arguments(['general-aip.py', 'path-error', 'general', 'zip'])
        errors = ['AIPs directory argument is not a valid directory.',
                  'Cannot check for the metadata.csv because the AIPs directory has an error.']
        expected = (None, 'general', True, None, None, errors)
        self.assertEqual(expected, result, "Problem with test for required argument, error")


if __name__ == "__main__":
    unittest.main()
