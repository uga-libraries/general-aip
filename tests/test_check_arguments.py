"""Testing for the function check_arguments, which tests the correctness of user input from sys.argv and
 returns a list with the variable values and error messages, if any.

 For arguments with many possible correct values, most values are present in one of the tests for the other arguments,
 but it didn't seem worth having a separate correct test for each one given the large number.
 """

import os
import unittest
from aip_functions import check_arguments


class TestCheckArguments(unittest.TestCase):

    def test_correct(self):
        """Test for when all required arguments are correct and the metadata.csv is present"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'general', 'zip'])
        expected = (aips_dir, 'general', True, None, os.path.join(aips_dir, 'metadata.csv'), [])
        self.assertEqual(expected, result, "Problem with test for correct")

    def test_correct_optional(self):
        """Test for when all required arguments and optional argument are correct and the metadata.csv is present"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'av', 'no-zip', 'dpx'])
        expected = (aips_dir, 'av', False, 'dpx', os.path.join(aips_dir, 'metadata.csv'), [])
        self.assertEqual(expected, result, "Problem with test for required argument only, correct")

    def test_metadata_missing(self):
        """Test for when the arguments are correct but the metadata.csv is not in the expected location"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'no_metadata_csv')
        result = check_arguments(['general-aip.py', aips_dir, 'web', 'zip'])
        errors = ['Missing the required file metadata.csv in the AIPs directory.']
        expected = (aips_dir, 'web', True, None, None, errors)
        self.assertEqual(expected, result, "Problem with test for metadata_missing")

    def test_no_argument(self):
        """Test for when the user supplies no arguments. There is still one value in sys.argv, the script name"""
        result = check_arguments(['general-aip.py'])
        errors = ['Required arguments are missing: aips_directory, aip_type, and to_zip.',
                  'Cannot check for the metadata.csv because the AIPs directory has an error.']
        expected = (None, None, None, None, None, errors)
        self.assertEqual(expected, result, "Problem with test for no argument provided")

    def test_first_error(self):
        """Test for when the first argument (aips_directory) is not a valid path"""
        result = check_arguments(['general-aip.py', 'aips-dir-path-error', 'av', 'zip', 'mkv'])
        errors = ['Provided aips_directory "aips-dir-path-error" is not a valid directory.',
                  'Cannot check for the metadata.csv because the AIPs directory has an error.']
        expected = (None, 'av', True, 'mkv', None, errors)
        self.assertEqual(expected, result, "Problem with test for first argument error")

    def test_second_error(self):
        """Test for when the second argument (aip_type) is not one of the expected values"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'type-error', 'no-zip', 'mov'])
        errors = ['Provided aip_type "type-error" is not an expected value (av, general, web).']
        expected = (aips_dir, None, False, 'mov', os.path.join(aips_dir, 'metadata.csv'), errors)
        self.assertEqual(expected, result, "Problem with test for second argument error")

    def test_third_error(self):
        """Test for when the third argument (to_zip) is not one of the expected values"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'av', 'zip-error', 'mp4'])
        errors = [f'Provided to_zip "zip-error" is not an expected value (no-zip, zip).']
        expected = (aips_dir, 'av', None, 'mp4', os.path.join(aips_dir, 'metadata.csv'), errors)
        self.assertEqual(expected, result, "Problem with test for third argument error")

    def test_fourth_error(self):
        """Test for when the fourth argument (workflow) is not one of the expected values"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'general', 'zip', 'wf-error'])
        errors = ['Provided workflow "wf-error" is not an expected value (dpx, mkv, mkv-filmscan, mov, mp4, mxf, wav)']
        expected = (aips_dir, 'general', True, None, os.path.join(aips_dir, 'metadata.csv'), errors)
        self.assertEqual(expected, result, "Problem with test for fourth argument error")

    def test_all_error(self):
        """Test for when all arguments are not expected values"""
        result = check_arguments(['general-aip.py', 'path-error', 'type-error', 'zip-error', 'wf-error'])
        errors = ['Provided aips_directory "path-error" is not a valid directory.',
                  'Provided aip_type "type-error" is not an expected value (av, general, web).',
                  'Provided to_zip "zip-error" is not an expected value (no-zip, zip).',
                  'Provided workflow "wf-error" is not an expected value (dpx, mkv, mkv-filmscan, mov, mp4, mxf, wav)',
                  'Cannot check for the metadata.csv because the AIPs directory has an error.']
        expected = (None, None, None, None, None, errors)
        self.assertEqual(expected, result, "Problem with test for all error")

    def test_extra(self):
        """Test for when there are more arguments than expected (more than 4)"""
        aips_dir = os.path.join(os.getcwd(), 'check_arguments', 'aips_dir')
        result = check_arguments(['general-aip.py', aips_dir, 'av', 'no-zip', 'mxf', 'extra', 'extra2'])
        errors = ['Too many script arguments. The maximum expected is 4.']
        expected = (aips_dir, 'av', False, 'mxf', os.path.join(aips_dir, 'metadata.csv'), errors)
        self.assertEqual(expected, result, "Problem with test for extra arguments")


if __name__ == "__main__":
    unittest.main()
