"""Testing for the function test_check_metadata.csv, which takes data from a read CSV as input,
tests if it meets UGA requirements, and returns either an empty list (no errors) or a list of errors.

In production, the file must be named metadata.csv, but for testing a prefix is added with the test type.
"""

import os
import unittest
from aip_functions import check_metadata_csv


class TestCheckMetadataCSV(unittest.TestCase):

    def test_correct(self):
        """Test for a metadata.csv with the correct information"""
        # Makes the variable needed for function parameters and runs the function.
        aip_metadata_csv = os.path.join('check_metadata_csv', 'correct_metadata.csv')
        metadata_df, metadata_errors = check_metadata_csv(aip_metadata_csv, 'check_metadata_csv')

        # Verifies the df has the expected contents.
        # Only checking the returned df when there are no errors, since any error will quit the script.
        df_list = [metadata_df.columns.tolist()] + metadata_df.values.tolist()
        expected = [['Department', 'Collection', 'Folder', 'AIP_ID', 'Title', 'Rights', 'Version'],
                    ['test', 't-coll', 'aip-1', 'aip1', 'title-1', 'http://rightsstatements.org/vocab/InC/1.0/', '1'],
                    ['test', 't-coll', 'aip-2', 'aip2', 'title-2', 'http://rightsstatements.org/vocab/InC/1.0/', '1'],
                    ['test', 't-coll', 'aip-3', 'aip3', 'title-3', 'http://rightsstatements.org/vocab/InC/1.0/', '1']]
        self.assertEqual(expected, df_list, "Problem with test for correct, df")

        # Verifies the errors list has the expected values.
        expected = []
        self.assertEqual(expected, metadata_errors, "Problem with test for correct, errors list")

    def test_error_columns(self):
        """Test for the column names in metadata.csv not matching the expected values"""
        # Makes the variable needed for function parameters and runs the function.
        aip_metadata_csv = os.path.join('check_metadata_csv', 'error_columns_metadata.csv')
        metadata_df, metadata_errors = check_metadata_csv(aip_metadata_csv, 'check_metadata_csv')

        # Verifies the errors list has the expected values.
        expected = ['The columns in the metadata.csv do not match the required values or order.',
                    'Required: Department, Collection, Folder, AIP_ID, Title, Rights, Version',
                    'Current:  AIP_ID, Dept, Coll, Current, title, Rights_Statement, Version',
                    'Since the columns are not correct, did not check the column values.']
        self.assertEqual(expected, metadata_errors, "Problem with test for error_columns, errors list")

    def test_error_csv_only(self):
        """Test for AIP folders that are only in the metadata.csv and not in the AIPs directory"""
        # Makes the variable needed for function parameters and runs the function.
        aip_metadata_csv = os.path.join('check_metadata_csv', 'error_csv_only_metadata.csv')
        metadata_df, metadata_errors = check_metadata_csv(aip_metadata_csv, 'check_metadata_csv')

        # Verifies the errors list has the expected values.
        expected = ['Folder(s) in metadata csv but not in aips_directory: aip-4.']
        self.assertEqual(expected, metadata_errors, "Problem with test for error_csv_only, errors list")

    def test_error_directory_only(self):
        """Test for AIP folders that are only in the AIPs directory and not the metadata.csv"""
        # Makes the variable needed for function parameters and runs the function.
        aip_metadata_csv = os.path.join('check_metadata_csv', 'error_directory_only_metadata.csv')
        metadata_df, metadata_errors = check_metadata_csv(aip_metadata_csv, 'check_metadata_csv')

        # Verifies the errors list has the expected values.
        expected = ['Folder(s) in aips_directory but not in metadata_csv: aip-1, aip-3.']
        self.assertEqual(expected, metadata_errors, "Problem with test for error_directory_only, errors list")

    def test_error_duplicate_folders(self):
        """Test for AIPs that are in the metadata.csv more than once"""
        # Makes the variable needed for function parameters and runs the function.
        aip_metadata_csv = os.path.join('check_metadata_csv', 'error_duplicate_metadata.csv')
        metadata_df, metadata_errors = check_metadata_csv(aip_metadata_csv, 'check_metadata_csv')

        # Verifies the errors list has the expected values.
        expected = ['Duplicate folder(s): aip-1, aip-2, aip-3.']
        self.assertEqual(expected, metadata_errors, "Problem with test for error_duplicate_folders, errors list")

    def test_error_group(self):
        """Test for departments in the metadata.csv which are not ARCHive groups (from the configuration file)"""
        # Makes the variable needed for function parameters and runs the function.
        aip_metadata_csv = os.path.join('check_metadata_csv', 'error_group_metadata.csv')
        metadata_df, metadata_errors = check_metadata_csv(aip_metadata_csv, 'check_metadata_csv')

        # Verifies the errors list has the expected values.
        expected = ['banana is not an ARCHive group.', 'Brown is not an ARCHive group.']
        self.assertEqual(expected, metadata_errors, "Problem with test for error_group, errors list")

    def test_error_rights(self):
        """Test for rights in the metadata.csv that are not Creative Commons or RightsStatements.org"""
        # Makes the variable needed for function parameters and runs the function.
        aip_metadata_csv = os.path.join('check_metadata_csv', 'error_rights_metadata.csv')
        metadata_df, metadata_errors = check_metadata_csv(aip_metadata_csv, 'check_metadata_csv')

        # Verifies the errors list has the expected values.
        expected = ['InC is not Creative Commons or RightsStatement.org.',
                    'BLANK is not Creative Commons or RightsStatement.org.']
        self.assertEqual(expected, metadata_errors, "Problem with test for error_rights, errors list")


if __name__ == "__main__":
    unittest.main()
