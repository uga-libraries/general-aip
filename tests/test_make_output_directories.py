"""Testing for the function make_output_directories, which creates three directories in the current directory.
It does not have any inputs and returns nothing."""

import os
import unittest
from aip_functions import make_output_directories


class TestMakeOutputDirectories(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the three script output folders.
        """
        os.rmdir(os.path.join("..", "aips-to-ingest"))
        os.rmdir(os.path.join("..", "fits-xml"))
        os.rmdir(os.path.join("..", "preservation-xml"))

    def test_aips_present(self):
        """
        Test for running the function when the aips-to-ingest folder already exists.
        Result for testing is a list of new folders in the parent directory of the current directory.
        """
        # Makes the aips-to-ingest folder.
        os.mkdir(os.path.join("..", "aips-to-ingest"))

        # Saves a list of what is in the parent directory before and after running the function
        # to calculate which directories were added by the function.
        parent_directory_before = os.listdir("..")
        make_output_directories()
        parent_directory_after = os.listdir("..")

        # Calculates the difference between the two directory prints and sorts so the values are predictable
        # and compares that to the expected result.
        result = list(set(parent_directory_after) - set(parent_directory_before))
        result.sort()
        expected = ["fits-xml", "preservation-xml"]
        self.assertEqual(result, expected, "Problem with make_output_directories, aips-to-ingest present")

    def test_all_present(self):
        """
        Test for running the function when all three folders already exist.
        Result for testing is a list of new folders in the parent directory of the current directory.
        """
        # Makes the three input folders.
        os.mkdir(os.path.join("..", "aips-to-ingest"))
        os.mkdir(os.path.join("..", "fits-xml"))
        os.mkdir(os.path.join("..", "preservation-xml"))

        # Saves a list of what is in the parent directory before and after running the function
        # to calculate which directories were added by the function.
        parent_directory_before = os.listdir("..")
        make_output_directories()
        parent_directory_after = os.listdir("..")

        # Calculates the difference between the two directory prints and sorts so the values are predictable
        # and compares that to the expected result.
        result = list(set(parent_directory_after) - set(parent_directory_before))
        result.sort()
        expected = []
        self.assertEqual(result, expected, "Problem with make_output_directories, all present")

    def test_none_present(self):
        """
        Test for running the function when none of the three folders already exist.
        Result for testing is a list of new folders in the parent directory of the current directory.
        """
        # Saves a list of what is in the parent directory before and after running the function
        # to calculate which directories were added by the function.
        parent_directory_before = os.listdir("..")
        make_output_directories()
        parent_directory_after = os.listdir("..")

        # Calculates the difference between the two directory prints and sorts so the values are predictable
        # and compares that to the expected result.
        result = list(set(parent_directory_after) - set(parent_directory_before))
        result.sort()
        expected = ["aips-to-ingest", "fits-xml", "preservation-xml"]
        self.assertEqual(result, expected, "Problem with make_output_directories")


if __name__ == "__main__":
    unittest.main()
