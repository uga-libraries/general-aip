"""Testing for the function check_arguments, which tests the correctness of user input from sys.argv and
 returns a tuple with the variable values and error messages, if any."""
#TODO function updated for AV

import os
import unittest
from aip_functions import check_arguments


class TestCheckArguments(unittest.TestCase):

    def setUp(self):
        """
        Makes a file named metadata.csv in the AIPs directory, which is expected by the script.
        This file doesn't have the correct content, but having the correct file name is enough for these tests.
        """
        self.csv_path = os.path.join(os.getcwd(), "metadata.csv")
        with open(self.csv_path, "w") as file:
            file.write("File for testing metadata.csv is present")

    def tearDown(self):
        """
        Deletes the metadata.csv file, if it is still present.
        The file is already deleted within the test for the metadata.csv error to generate the error.
        """
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    def test_metadata_missing(self):
        """
        Test for if the aips_directory (the only required argument) is present and the path is valid,
        but the metadata.csv is not in the expected location.
        """
        # Deletes the metadata.csv file made by setUp.
        os.remove(self.csv_path)
        result = check_arguments(["general-aip.py", os.getcwd()])
        errors = ["Missing the required file metadata.csv in the AIPs directory."]
        expected = (os.getcwd(), True, None, errors)
        self.assertEqual(result, expected, "Problem with test for missing metadata.csv")

    def test_no_argument(self):
        """
        Test for if the user supplies no arguments.
        There is still one value in sys.argv, the script name.
        """
        result = check_arguments(["general-aip.py"])
        errors = ["AIPs directory argument is missing.",
                  "Cannot check for the metadata.csv because the AIPs directory has an error."]
        expected = (None, True, None, errors)
        self.assertEqual(result, expected, "Problem with test for no argument provided")

    def test_optional_argument(self):
        """
        Test for if the user includes the correct optional argument, no-zip.
        The aips_directory is correct and metadata.csv is in the expected location.
        """
        result = check_arguments(["general-aip.py", os.getcwd(), "no-zip"])
        expected = (os.getcwd(), False, self.csv_path, [])
        self.assertEqual(result, expected, "Problem with test for optional argument included, correct")

    def test_optional_argument_error(self):
        """
        Test for if the user includes the optional argument but it is not the expected value.
        """
        result = check_arguments(["general-aip.py", os.getcwd(), "error"])
        errors = ["Unexpected value for the second argument. If provided, should be 'no-zip'."]
        expected = (os.getcwd(), None, self.csv_path, errors)
        self.assertEqual(result, expected, "Problem with test for optional argument included, error")

    def test_required_argument(self):
        """
        Test for if the aips_directory (the only required argument) is present and the path is valid.
        """
        result = check_arguments(["general-aip.py", os.getcwd()])
        expected = (os.getcwd(), True, self.csv_path, [])
        self.assertEqual(result, expected, "Problem with test for required argument only, correct")

    def test_required_argument_error(self):
        """
        Test for if the aips_directory (the only required argument) is present but the path is not valid.
        """
        result = check_arguments(["general-aip.py", "path-error"])
        errors = ["AIPs directory argument is not a valid directory.",
                  "Cannot check for the metadata.csv because the AIPs directory has an error."]
        expected = (None, True, None, errors)
        self.assertEqual(result, expected, "Problem with test for required argument only, error")


if __name__ == "__main__":
    unittest.main()
