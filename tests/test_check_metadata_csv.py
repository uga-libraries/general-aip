"""Testing for the function test_check_metadata.csv, which takes data from a read CSV as input,
tests if it meets UGA requirements, and returns either an empty list (no errors) or a list of errors.

In production, the file must be named metadata.csv, but for testing a prefix is added with the test type."""

import csv
import os
import shutil
import unittest
from aip_functions import check_metadata_csv


def run_function(csv_name):
    """
    Reads the CSV, runs the function with the read data, and returns the function output.
    """
    aip_dir = os.path.join(os.getcwd(), 'check_metadata_csv')
    with open(os.path.join(aip_dir, csv_name)) as open_metadata:
        read_metadata = csv.reader(open_metadata)
        output = check_metadata_csv(read_metadata, aip_dir)
    return output


class TestCheckMetadataCSV(unittest.TestCase):

    def test_correct(self):
        """
        Test for a metadata.csv with valid information 
        and column case matches the README instructions exactly.
        """
        result = run_function('correct_same_case_metadata.csv')
        expected = []
        self.assertEqual(result, expected, "Problem with test for correct_same_case_metadata.csv")

    def test_correct_case_difference(self):
        """
        Test for a metadata.csv with valid information
        and the column case doesn't match the README instructions. This is not an error.
        """
        result = run_function('correct_diff_case_metadata.csv')
        expected = []
        self.assertEqual(result, expected, "Problem with test for correct_diff_case_metadata.csv")

    def test_error_columns(self):
        """
        Test for the column names in metadata.csv not matching the expected values.
        """
        result = run_function('error_column_order_metadata.csv')
        expected = ['The columns in the metadata.csv do not match the required values or order.',
                    'Required: Department, Collection, Folder, AIP_ID, Title, Version',
                    'Current:  AIP_ID, Department, Collection, Folder, Title, Version',
                    'Since the columns are not correct, did not check the column values.']
        self.assertEqual(result, expected, "Problem with test for error, columns")

    def test_error_group(self):
        """
        Test for departments in the metadata.csv which are not ARCHive groups (from the configuration file).
        """
        result = run_function('error_group_metadata.csv')
        expected = ['Brown is not an ARCHive group.', 'banana is not an ARCHive group.']
        self.assertEqual(result, expected, "Problem with test for error, group")

    def test_error_repeated_folders(self):
        """
        Test for AIPs that are in the metadata.csv more than once.
        """
        result = run_function('error_repeat_metadata.csv')
        expected = ['aip-2 is in the metadata.csv folder column more than once.',
                    'aip-3 is in the metadata.csv folder column more than once.']
        self.assertEqual(result, expected, "Problem with test for error, repeated folders")

    def test_error_csv_only(self):
        """
        Test for AIP folders that are only in the metadata.csv and not in the AIPs directory.
        """
        result = run_function('error_csv_only_metadata.csv')
        expected = ['aip-4 is in metadata.csv and missing from the AIPs directory.',
                    'aip-5 is in metadata.csv and missing from the AIPs directory.']
        self.assertEqual(result, expected, "Problem with test for error, CSV only")

    def test_error_directory_only(self):
        """
        Test for AIP folders that are only in the AIPs directory and not the metadata.csv.
        """
        result = run_function('error_directory_only_metadata.csv')
        expected = ['aip-1 is in the AIPs directory and missing from metadata.csv.',
                    'aip-3 is in the AIPs directory and missing from metadata.csv.']
        self.assertEqual(result, expected, "Problem with test for error, directory only")


if __name__ == "__main__":
    unittest.main()
