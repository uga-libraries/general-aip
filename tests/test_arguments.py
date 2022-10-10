"""Testing for the function check_arguments, which tests the correctness of input from sys.argv and
 returns variable values and error messages, if any."""

import os
import unittest
from scripts.aip_functions import check_arguments


class TestCheckArguments(unittest.TestCase):

    def test_one_arg(self):
        """
        Test for if the user supplies no arguments. There is still one argument in sys.argv, the script name.
        """
        result = check_arguments(['general-aip.py'])
        expected = (None, True, None, ['AIPs directory argument is missing.',
                                       'Cannot check for the metadata.csv in the AIPs directory because the AIPs directory has an error.'])
        self.assertEqual(result, expected, 'Problem with detecting error for one argument')

    def test_two_arg_no_err(self):
        """
        Test for if the user supplies the aips_directory (valid) and the metadata.csv is also in the expected location.
        """
        metadata_csv_path = os.path.join(os.getcwd(), 'metadata.csv')
        with open(metadata_csv_path, "w") as file:
            file.write("Sample file")
        result = check_arguments(['general-aip.py', os.getcwd()])
        expected = (os.getcwd(), True, metadata_csv_path, [])
        self.assertEqual(result, expected, 'Problem with correct aips_directory and metadata.csv')
        os.remove(metadata_csv_path)

    def test_two_arg_metadata_err(self):
        """
        Test for if the user supplies the aips_directory (valid) and the metadata.csv is not in the expected location.
        """
        result = check_arguments(['general-aip.py', os.getcwd()])
        expected = (os.getcwd(), True, None, ['Missing the required file metadata.csv in the AIPs directory.'])
        self.assertEqual(result, expected, 'Problem with correct aips_directory and missing metadata.csv')

    def test_two_arg_aips_err(self):
        """
        Test for if the user supplies the aips_directory but the path is not valid.
        """
        result = check_arguments(['general-aip.py', 'path-error'])
        expected = (None, True, None, ['AIPs directory argument is not a valid directory.',
                                       'Cannot check for the metadata.csv in the AIPs directory because the AIPs directory has an error.'])
        self.assertEqual(result, expected, 'Problem with incorrect aips_directory')


if __name__ == '__main__':
    unittest.main()