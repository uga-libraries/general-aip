"""Testing for the function make_output_directories, which creates three directories in the current directory.
It does not have any inputs and returns nothing."""

import os
import unittest
from aip_functions import make_output_directories


class TestMakeOutputDirectories(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the three script output folders, if they exist.
        """
        output_folders = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        for output_folder in output_folders:
            folder_path = os.path.join(os.getcwd(), 'aip_staging_location', output_folder)
            if os.path.exists(folder_path):
                os.rmdir(folder_path)

    def test_aips_present(self):
        """
        Test for running the function when the aips-ready-to-ingest folder already exists.
        """
        # Makes the aips-ready-to-ingest folder.
        aip_staging = os.path.join(os.getcwd(), "aip_staging_location")
        os.mkdir(os.path.join(aip_staging, "aips-ready-to-ingest"))

        # Saves a list of what is in the aip staging directory before and after running the function
        # to calculate which directories were added by the function.
        staging_before = os.listdir(aip_staging)
        make_output_directories(aip_staging, "general")
        staging_after = os.listdir(aip_staging)

        # Calculates the difference between the two lists and sorts so the values are predictable.
        result = list(set(staging_after) - set(staging_before))
        result.sort()
        expected = ["fits-xmls", "preservation-xmls"]
        self.assertEqual(result, expected, "Problem with make_output_directories, aips-ready-to-ingest present")

    def test_all_present(self):
        """
        Test for running the function when all three folders already exist.
        """
        # Makes the three input folders.
        aip_staging = os.path.join(os.getcwd(), "aip_staging_location")
        os.mkdir(os.path.join(aip_staging, "aips-ready-to-ingest"))
        os.mkdir(os.path.join(aip_staging, "fits-xmls"))
        os.mkdir(os.path.join(aip_staging, "preservation-xmls"))

        # Saves a list of what is in the aip staging directory before and after running the function
        # to calculate which directories were added by the function.
        staging_before = os.listdir(aip_staging)
        make_output_directories(aip_staging, "general")
        staging_after = os.listdir(aip_staging)

        # Calculates the difference between the two lists and sorts so the values are predictable.
        result = list(set(staging_after) - set(staging_before))
        result.sort()
        expected = []
        self.assertEqual(result, expected, "Problem with make_output_directories, all present")

    def test_none_present(self):
        """
        Test for running the function when none of the three folders already exist.
        """
        # Saves a list of what is in the aip staging directory before and after running the function
        # to calculate which directories were added by the function.
        aip_staging = os.path.join(os.getcwd(), "aip_staging_location")
        staging_before = os.listdir(aip_staging)
        make_output_directories(aip_staging, "general")
        staging_after = os.listdir(aip_staging)

        # Calculates the difference between the two lists and sorts so the values are predictable.
        result = list(set(staging_after) - set(staging_before))
        result.sort()
        expected = ["aips-ready-to-ingest", "fits-xmls", "preservation-xmls"]
        self.assertEqual(result, expected, "Problem with make_output_directories, none present")


if __name__ == "__main__":
    unittest.main()
