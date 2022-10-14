"""Testing for the function check_arguments, which tests the correctness of input from sys.argv and
 returns variable values and error messages, if any."""

import os
import unittest
from scripts.aip_functions import check_arguments


class TestCheckArguments(unittest.TestCase):

    def setUp(self):
        """
        Makes a file named metadata.csv in the AIPs directory, which is expected by the script.
        This file doesn't have the correct content, but having the correct file name is enough for these tests.
        """
        self.csv_path = os.path.join(os.getcwd(), 'metadata.csv')
        with open(self.csv_path, "w") as file:
            file.write("File for testing metadata.csv is present")

    def test_one_arg(self):
        """
        Test for if the user supplies no arguments. There is still one argument in sys.argv, the script name.
        """
        result = check_arguments(['general-aip.py'])
        expected = (None, True, None, ['AIPs directory argument is missing.',
                                       'Cannot check for the metadata.csv in the AIPs directory because the AIPs directory has an error.'])
        self.assertEqual(result, expected, 'Problem with no aips_directory')

    def test_two_arg_no_err(self):
        """
        Test for if the user supplies a valid aips_directory and the metadata.csv is also in the expected location.
        """
        result = check_arguments(['general-aip.py', os.getcwd()])
        expected = (os.getcwd(), True, self.csv_path, [])
        self.assertEqual(result, expected, 'Problem with correct aips_directory and correct metadata.csv')

    def test_two_arg_aips_err(self):
        """
        Test for if the user supplies the aips_directory but the path is not valid.
        """
        result = check_arguments(['general-aip.py', 'path-error'])
        expected = (None, True, None, ['AIPs directory argument is not a valid directory.',
                                       'Cannot check for the metadata.csv in the AIPs directory because the AIPs directory has an error.'])
        self.assertEqual(result, expected, 'Problem with incorrect aips_directory')

    def test_two_arg_metadata_err(self):
        """
        Test for if the user supplies a valid aips_directory and the metadata.csv is not in the expected location.
        """
        os.remove(self.csv_path)
        result = check_arguments(['general-aip.py', os.getcwd()])
        expected = (os.getcwd(), True, None, ['Missing the required file metadata.csv in the AIPs directory.'])
        self.assertEqual(result, expected, 'Problem with correct aips_directory and missing metadata.csv')

    def test_three_arg_no_err(self):
        """
        Test for if the user includes the correct optional argument, no-zip.
        The aips_directory is correct and metadata.csv is in the expected location.
        """
        result = check_arguments(['general-aip.py', os.getcwd(), 'no-zip'])
        expected = (os.getcwd(), False, self.csv_path, [])
        self.assertEqual(result, expected, 'Problem with correct no-zip')

    def test_three_arg_err(self):
        """
        Test for if the user includes the optional argument but it is not the expected value.
        The aips_directory is correct and metadata.csv is in the expected location.
        """
        result = check_arguments(['general-aip.py', os.getcwd(), 'error'])
        expected = (os.getcwd(), None, self.csv_path, ['Unexpected value for the second argument. If provided, should be "no-zip".'])
        self.assertEqual(result, expected, 'Problem with wrong value for no-zip argument')


if __name__ == '__main__':
    unittest.main()