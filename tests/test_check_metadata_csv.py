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
        Changes the current directory so there isn't a permissions error for deleting aips_directory
        when it is in the current directory.
        """
        os.chdir('..')
        shutil.rmtree('aips_directory')

    def test_correct_case_match(self):
        """
        Test for a metadata.csv with valid information and column case matches the template exactly.
        Result for testing is the list returned by check_metadata_csv().
        """
        with open(os.path.join('..', 'metadata_csv', 'correct_same_case_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)

        expected = []

        self.assertEqual(result, expected, 'Problem with correct_same_case_metadata.csv')

    def test_correct_case_difference(self):
        """
        Test for a metadata.csv with valid information, but the column titles are all lowercase or uppercase.
        This doesn't match the template but is not an error.
        Result for testing is the list returned by check_metadata_csv().
        """
        with open(os.path.join('..', 'metadata_csv', 'correct_diff_case_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)

        expected = []

        self.assertEqual(result, expected, 'Problem with correct_diff_case_metadata.csv')

    def test_column_order_error(self):
        """
        Test for the column names in metadata.csv not matching the expected order.
        Result for testing is the list returned by check_metadata_csv().
        """
        with open(os.path.join('..', 'metadata_csv', 'error_column_order_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)

        expected = ['The columns in the metadata.csv do not match the required values or order.',
                    'Required: Department, Collection, Folder, AIP_ID, Title, Version',
                    'Current:  AIP_ID, Department, Collection, Folder, Title, Version',
                    'Since the columns are not correct, did not check the column values.']

        self.assertEqual(result, expected, 'Problem with error_column_order_metadata.csv')

    def test_group_error(self):
        """
        Test for departments in the metadata.csv which are not ARCHive groups (from the configuration file).
        Result for testing is the list returned by check_metadata_csv().
        """
        with open(os.path.join('..', 'metadata_csv', 'error_group_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)

        expected = ['Brown is not an ARCHive group.', 'banana is not an ARCHive group.']

        self.assertEqual(result, expected, 'Problem with error_group_metadata.csv')

    def test_repeat_folders_error(self):
        """
        Test for AIPs that are in the metadata.csv more than once, based on the folder.
        Result for testing is the list returned by check_metadata_csv().
        """
        with open(os.path.join('..', 'metadata_csv', 'error_repeat_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)

        expected = ['aip-2 is in the metadata.csv folder column more than once.',
                    'aip-3 is in the metadata.csv folder column more than once.']

        self.assertEqual(result, expected, 'Problem with error_repeat_metadata.csv')

    def test_csv_only_error(self):
        """
        Test for AIP folders that are only in the metadata.csv and not in the AIPs directory.
        Result for testing is the list returned by check_metadata_csv().
        """
        with open(os.path.join('..', 'metadata_csv', 'error_csv_only_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)

        expected = ['aip-4 is in metadata.csv and missing from the AIPs directory.',
                    'aip-5 is in metadata.csv and missing from the AIPs directory.']

        self.assertEqual(result, expected, 'Problem with error_csv_only_metadata.csv')

    def test_directory_only_error(self):
        """
        Test for AIP folders that are only in the AIPs directory and not the metadata.csv.
        Result for testing is the list returned by check_metadata_csv().
        """
        with open(os.path.join('..', 'metadata_csv', 'error_directory_only_metadata.csv')) as open_metadata:
            read_metadata = csv.reader(open_metadata)
            result = check_metadata_csv(read_metadata)

        expected = ['aip-1 is in the AIPs directory and missing from metadata.csv.',
                    'aip-3 is in the AIPs directory and missing from metadata.csv.']

        self.assertEqual(result, expected, 'Problem with error_directory_only_metadata.csv')


if __name__ == '__main__':
    unittest.main()
