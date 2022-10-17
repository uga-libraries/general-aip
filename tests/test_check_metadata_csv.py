"""Testing for the function test_check_metadata.csv, which takes data from a read CSV as input,
tests if it meets UGA requirements, and returns either an empty list (no errors) or a list of errors.

The CSVs used in testing are in the tests subfolder of the script repo.
In production, the file must be named metadata.csv, but for testing a prefix is added with the test type."""

import csv
import os
import shutil
import unittest
from scripts.aip_functions import check_metadata_csv


class TestCheckMetadataCSV(unittest.TestCase):

    def setUp(self):
        """
        Makes folders to serve as the AIPs directory and makes that the current directory.
        If a metadata.csv file is correct, it contains all the folders in the AIPs directory and nothing else.
        """
        os.mkdir('aips_directory')
        os.mkdir(os.path.join('aips_directory', 'aip-1'))
        os.mkdir(os.path.join('aips_directory', 'aip-2'))
        os.mkdir(os.path.join('aips_directory', 'aip-3'))

        os.chdir('aips_directory')

    def tearDown(self):
        """
        Deletes the folders used for the AIPs directory for testing.
        """
        os.chdir('..')
        shutil.rmtree('aips_directory')

    def test_correct_case_match(self):
        """
        Test for a metadata.csv with valid information and column case matches the template exactly.
        """
        with open(os.path.join('..', 'metadata_csv', 'correct_same_case_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)
        expected = []
        self.assertEqual(result, expected, 'Problem with correct_same_case_metadata.csv')

    # def test_correct_case_difference(self):
    #     """
    #     Test for a metadata.csv with valid information, but the column titles are all lowercase.
    #     This doesn't match the template but is not an error.
    #     """
    #     with open(os.path.join('metadata_csv', 'correct_diff_case_metadata.csv')) as open_metadata:
    #         read_metadata = csv.reader(open_metadata)
    #         result = check_metadata_csv(read_metadata)
    #     expected = []
    #     self.assertEqual(result, expected, 'Problem with correct_diff_case_metadata.csv')
    #
    # def test_column_order(self):
    #     """
    #     Test for the column names in metadata.csv not matching the expected order.
    #     This is an error.
    #     """
    #     with open(os.path.join('metadata_csv', 'column_order_metadata.csv')) as open_metadata:
    #         read_metadata = csv.reader(open_metadata)
    #         result = check_metadata_csv(read_metadata)
    #     expected = ['The columns in the metadata.csv do not match the required values or order.',
    #                 'Required: Department, Collection, Folder, AIP_ID, Title, Version',
    #                 'Current:  XXXX',
    #                 'Since the columns are not correct, did not check the column values.']
    #     self.assertEqual(result, expected, 'Problem with column_order_metadata.csv')
    #
    # def test_group(self):
    #     """
    #     Test for departments in the metadata.csv which are not ARCHive groups (from the configuration file).
    #     This is an error.
    #     """
    #     with open(os.path.join('metadata_csv', 'group_metadata.csv')) as open_metadata:
    #         read_metadata = csv.reader(open_metadata)
    #         result = check_metadata_csv(read_metadata)
    #     expected = ['XXXX is not an ARCHive group.',
    #                 'XXXX is not an ARCHive group.']
    #     self.assertEqual(result, expected, 'Problem with group_metadata.csv')
    #
    # def test_repeat_folders(self):
    #     """
    #     Test for AIPs that are in the metadata.csv more than once.
    #     This is an error.
    #     """
    #     with open(os.path.join('metadata_csv', 'repeat_metadata.csv')) as open_metadata:
    #         read_metadata = csv.reader(open_metadata)
    #         result = check_metadata_csv(read_metadata)
    #     expected = ['XXXX is in the metadata.csv folder column more than once.',
    #                 'XXXX is in the metadata.csv folder column more than once.']
    #     self.assertEqual(result, expected, 'Problem with repeat_metadata.csv')
    #
    # def test_csv_only(self):
    #     """
    #     Test for AIPs that are only in the metadata.csv and not in the AIPs directory.
    #     This is an error.
    #     """
    #     with open(os.path.join('metadata_csv', 'csv_only_metadata.csv')) as open_metadata:
    #         read_metadata = csv.reader(open_metadata)
    #         result = check_metadata_csv(read_metadata)
    #     expected = ['XXXX is in metadata.csv and missing from the AIPs directory.',
    #                 'XXXX is in metadata.csv and missing from the AIPs directory.']
    #     self.assertEqual(result, expected, 'Problem with csv_only_metadata.csv')
    #
    # def test_directory_only(self):
    #     """
    #     Test for AIPs that are only in the AIPs directory and not the metadata.csv.
    #     This is an error.
    #     """
    #     with open(os.path.join('metadata_csv', 'directory_only_metadata.csv')) as open_metadata:
    #         read_metadata = csv.reader(open_metadata)
    #         result = check_metadata_csv(read_metadata)
    #     expected = ['XXXX is in the AIPs directory and missing from metadata.csv.',
    #                 'XXXX is in the AIPs directory and missing from metadata.csv.']
    #     self.assertEqual(result, expected, 'Problem with directory_only_metadata.csv')


if __name__ == '__main__':
    unittest.main()
