"""Testing for the function validate_bag, which takes an AIP class instance as input and validates the AIPs bag.
There is error handling for if the bag is not valid.

NOTE: there is no test for writing the entire message to the log if the information is not in error.details
because we don"t know how to force that to happen.
"""

import datetime
import os
import pandas as pd
import shutil
import unittest
from aip_functions import AIP, log, validate_bag


def aip_log_list(log_path):
    """Make a list of rows within an aip log for comparing to the expected results"""
    log_df = pd.read_csv(log_path)
    log_df = log_df.fillna('BLANK')
    log_list = [log_df.columns.tolist()] + log_df.values.tolist()
    return log_list


def validation_log_list(aip_id):
    """Make a list of rows within a validation log for comparing to the expected results,
    sorting the list since bagit validation outputs are in an unpredictable order"""
    log_path = os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'bag_not_valid',
                            f'{aip_id}_bag_validation.txt')
    with open(log_path, 'r') as open_file:
        log_list = open_file.readlines()
        log_list.sort()
        return log_list


class TestValidateBag(unittest.TestCase):

    def tearDown(self):
        """Deletes the AIP log and bag_not_valid errors folder if they were made"""
        log_path = os.path.join(os.getcwd(), 'validate_bag', 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        error_path = os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors', 'bag_not_valid')
        if os.path.exists(error_path):
            shutil.rmtree(error_path)

    def test_not_valid_added(self):
        """Test for when a bag is not valid because files were added after it was bagged"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        # A copy of the bag is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'validate_bag')
        aip_staging = os.path.join(os.getcwd(), 'aip_staging_location')
        aip = AIP(aips_dir, 'test', None, 'not_valid', 'folder', 'general', 'test_not_001', 'title', 1, True)
        aip.log = {'Started': '2025-08-14 9:30AM', 'AIP': 'test_not_001', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'n/a', 'Package': 'n/a', 'Manifest': 'n/a',
                   'Complete': 'n/a'}
        log('header', aips_dir)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_bag_copy'), os.path.join(aips_dir, f'{aip.id}_bag'))
        validate_bag(aip, aip_staging)

        # Test that the AIP log has the expected contents.
        result = aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14 9:30AM', 'test_not_001', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Bag not valid (see log in bag_not_valid error folder)',
                     'BLANK', 'BLANK', 'Error during processing']]
        self.assertEqual(result, expected, "Problem with test for not_valid_added, AIP log")

        # Test that the AIP folder was moved to the error folder.
        result = os.path.exists(os.path.join(aip_staging, 'aips-with-errors', 'bag_not_valid', f'{aip.id}_bag'))
        self.assertEqual(result, True, "Problem with test for not_valid_added, error folder")

        # Test that the validation log has the expected contents.
        result = validation_log_list(aip.id)
        expected = ['Payload-Oxum validation failed. Expected 5 files and 122 bytes but found 7 files and 201 bytes']
        self.assertEqual(result, expected, "Problem with test for not_valid_added, validation log")

    def test_not_valid_deleted(self):
        """Test for when a bag is not valid because a file was deleted after it was bagged"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        # A copy of the bag is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'validate_bag')
        aip_staging = os.path.join(os.getcwd(), 'aip_staging_location')
        aip = AIP(aips_dir, 'test', None, 'not_valid', 'folder', 'general', 'test_not_002', 'title', 1, True)
        aip.log = {'Started': '2025-08-14 9:50AM', 'AIP': 'test_not_002', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'n/a', 'Package': 'n/a', 'Manifest': 'n/a',
                   'Complete': 'n/a'}
        log('header', aips_dir)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_bag_copy'), os.path.join(aips_dir, f'{aip.id}_bag'))
        validate_bag(aip, aip_staging)

        # Test that the AIP log has the expected contents.
        result = aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14 9:50AM', 'test_not_002', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Bag not valid (see log in bag_not_valid error folder)',
                     'BLANK', 'BLANK', 'Error during processing']]
        self.assertEqual(result, expected, "Problem with test for not_valid_deleted, AIP log")

        # Test that the AIP folder was moved to the error folder.
        result = os.path.exists(os.path.join(aip_staging, 'aips-with-errors', 'bag_not_valid', f'{aip.id}_bag'))
        self.assertEqual(result, True, "Problem with test for not_valid_deleted, error folder")

        # Test that the validation log has the expected contents.
        result = validation_log_list(aip.id)
        expected = ['Payload-Oxum validation failed. Expected 5 files and 122 bytes but found 4 files and 116 bytes']
        self.assertEqual(result, expected, "Problem with test for not_valid_deleted, validation log")

    def test_not_valid_edited(self):
        """Test for when a bag is not valid because files were edited after it was bagged"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        # A copy of the bag is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'validate_bag')
        aip_staging = os.path.join(os.getcwd(), 'aip_staging_location')
        aip = AIP(aips_dir, 'test', None, 'not_valid', 'folder', 'general', 'test_not_003', 'title', 1, True)
        aip.log = {'Started': '2025-08-14 9:55AM', 'AIP': 'test_not_003', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'n/a', 'Package': 'n/a', 'Manifest': 'n/a',
                   'Complete': 'n/a'}
        log('header', aips_dir)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_bag_copy'), os.path.join(aips_dir, f'{aip.id}_bag'))
        validate_bag(aip, aip_staging)

        # Test that the AIP log has the expected contents.
        result = aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14 9:55AM', 'test_not_003', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Bag not valid (see log in bag_not_valid error folder)',
                     'BLANK', 'BLANK', 'Error during processing']]
        self.assertEqual(result, expected, "Problem with test for not_valid_edited, AIP log")

        # Test that the AIP folder was moved to the error folder.
        result = os.path.exists(os.path.join(aip_staging, 'aips-with-errors', 'bag_not_valid', f'{aip.id}_bag'))
        self.assertEqual(result, True, "Problem with test for not_valid_edited, error folder")

        # Test that the validation log has the expected contents.
        result = validation_log_list(aip.id)
        expected = ['Payload-Oxum validation failed. Expected 5 files and 122 bytes but found 5 files and 143 bytes']
        self.assertEqual(result, expected, "Problem with test for not_valid_edited, validation log")

    def test_not_valid_md5(self):
        """Test for when a bag is not valid because the md5 changed for files after it was bagged"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        # A copy of the bag is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'validate_bag')
        aip_staging = os.path.join(os.getcwd(), 'aip_staging_location')
        aip = AIP(aips_dir, 'test', None, 'not_valid', 'folder', 'general', 'test_not_004', 'title', 1, True)
        aip.log = {'Started': '2025-08-14 10:00AM', 'AIP': 'test_not_004', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'n/a', 'Package': 'n/a', 'Manifest': 'n/a',
                   'Complete': 'n/a'}
        log('header', aips_dir)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_bag_copy'), os.path.join(aips_dir, f'{aip.id}_bag'))
        validate_bag(aip, aip_staging)

        # Test that the AIP log has the expected contents.
        result = aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14 10:00AM', 'test_not_004', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Bag not valid (see log in bag_not_valid error folder)',
                     'BLANK', 'BLANK', 'Error during processing']]
        self.assertEqual(result, expected, "Problem with test for not_valid_md5, AIP log")

        # Test that the AIP folder was moved to the error folder.
        result = os.path.exists(os.path.join(aip_staging, 'aips-with-errors', 'bag_not_valid', f'{aip.id}_bag'))
        self.assertEqual(result, True, "Problem with test for not_valid_md5, error folder")

        # Test that the validation log has the expected contents.
        result = validation_log_list(aip.id)
        expected = ['data\\metadata\\file.txt_fits.xml md5 validation failed: '
                    'expected="5d1bcdb4b339b3ebbe1de5eb002bf202" found="5d1bcdb4b339b3ebbe1de5eb772bf272"\n',
                    'data\\metadata\\test_valid_001_preservation.xml md5 validation failed: '
                    'expected="e0a3eddf0f12620b231bab4ea0fe4cc0" found="e7a3eddf0f12620b231bab4ea0fe4cc0"\n',
                    'data\\objects\\file1.txt md5 validation failed: expected="2f03b03630bf162930093f056f0f1583" '
                    'found="2f03b03637bf162937793f756f0f1583"\n',
                    'data\\objects\\file2.txt md5 validation failed: expected="d10ec0d49f924ed60c041089491b099e" '
                    'found="d17ec7d49f924ed60c041789491b099e"\n']
        self.assertEqual(result, expected, "Problem with test for not_valid_md5, validation log")

    def test_valid(self):
        """Test for when the bag is valid"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'validate_bag')
        aip_staging = os.path.join(os.getcwd(), 'aip_staging_location')
        aip = AIP(aips_dir, 'test', None, 'valid', 'folder', 'general', 'test_valid_001', 'title', 1, True)
        validate_bag(aip, aip_staging)

        # Test for the AIP log.
        # Since the log for bagging includes a timestamp, assert cannot require an exact match.
        result = aip.log['BagValid']
        expected = f'Bag valid on {datetime.date.today()}'
        self.assertIn(expected, result, "Problem with valid")


if __name__ == "__main__":
    unittest.main()
