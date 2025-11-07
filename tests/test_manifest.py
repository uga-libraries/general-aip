"""Testing for the function manifest, which takes an AIP class instance as input,
calculates the MD5 for the tar.bz2 version of the AIP, and adds that to the manifest.
There is error handling for if the .tar.bz2 version of the AIP doesn't exist and
for errors from the tool which generates the MD5.

NOTE: test_av only works on a Mac and is commented out by default.

NOTE: was not able to make a test for md5deep error handling.
The only way to cause an error is give it an incorrect path, but that is caught at an earlier step.
We plan to stop using md5deep fairly soon, so leaving that without a test.
"""

from datetime import datetime
import os
import pandas as pd
import shutil
import unittest
from aip_functions import AIP, log, manifest
from test_script import make_aip_log_list


def make_manifest_list(path):
    """Reads the manifest and returns a list of lists, where each list is a row in the manifest"""
    df = pd.read_csv(path, sep=r'\s+')
    df = df.fillna('BLANK')
    manifest_list = [df.columns.to_list()] + df.values.tolist()
    return manifest_list


class TestManifest(unittest.TestCase):

    def tearDown(self):
        """Deletes the AIP log and manifest, if made"""
        log_path = os.path.join(os.getcwd(), 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        date = datetime.now().strftime("%Y-%m-%d")

        # Deletes non-AV manifests (saved in aips-ready-to-ingest)
        manifest_list = [f'manifest_tests_hargrett_{date}.txt', f'manifest_tests_magil_{date}.txt',
                         f'manifest_tests_russell_{date}.txt']
        aip_folder_path = os.path.join(os.getcwd(), 'manifest', 'staging', 'aips-ready-to-ingest')
        for manifest_name in manifest_list:
            if os.path.exists(os.path.join(aip_folder_path, manifest_name)):
                os.remove(os.path.join(aip_folder_path, manifest_name))

        # Deletes AV manifest (saved in md5-manifests-for-aips)
        av_manifest_path = os.path.join(os.getcwd(), 'manifest', 'staging', 'md5-manifests-for-aips',
                                        f'manifest_tests_bmac_{date}.txt')
        if os.path.exists(av_manifest_path):
            os.remove(av_manifest_path)

        # Deletes the copy of the AV aip, which is copied to 2 folders when the test is run on a mac
        # and to an errors folder when the test is run on Windows.
        locations = [os.path.join(os.getcwd(), 'manifest', 'staging', 'aips-with-errors', 'copy_to_ingest_failed'),
                     os.path.join(os.getcwd(), 'manifest', 'staging', 'aips-already-on-ingest-server'),
                     os.path.join(os.getcwd(), 'ingest')]
        for location in locations:
            tar_path = os.path.join(location, 'rabbitbox_010_bag.20000.tar')
            if os.path.exists(tar_path):
                os.remove(tar_path)

    # def test_av(self):
    #     """Test for an AV AIP, which has the manifest saved to a different location
    #     NOTE: this only works if the test is run on a Mac, as it requires rsync"""
    #     # Makes the test input and runs the function.
    #     # A copy of the test file is made since in av mode it will be moved to a different location in staging.
    #     # The AIP log is updated as if previous steps have run correctly.
    #     aips_dir = os.getcwd()
    #     aip_staging = os.path.join(os.getcwd(), 'manifest', 'staging')
    #     shutil.copy2(os.path.join(aip_staging, 'aips-ready-to-ingest', 'copy_rabbitbox_010_bag.20000.tar'),
    #                  os.path.join(aip_staging, 'aips-ready-to-ingest', 'rabbitbox_010_bag.20000.tar'))
    #     aip = AIP(aips_dir, 'bmac', 'wav', 'rabbitbox', 'folder', 'av', 'rabbitbox_010', 'title', 1, False)
    #     aip.size = 20000
    #     aip.log = {'Started': '2025-09-08 01:25:01.000000', 'AIP': 'rabbitbox_010', 'Deletions': 'No files deleted',
    #                'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
    #                'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'Valid', 'Package': 'Success',
    #                'Manifest': 'n/a', 'Complete': 'n/a'}
    #     log('header', aips_dir)
    #     manifest(aip, aip_staging, os.path.join(os.getcwd(), os.path.join(os.getcwd(), 'ingest')))
    #
    #     # Test for the manifest.
    #     manifest_name = f'manifest_tests_bmac_{datetime.now().strftime("%Y-%m-%d")}.txt'
    #     result = make_manifest_list(os.path.join(aip_staging, 'md5-manifests-for-aips', manifest_name))
    #     expected = [['629f0e1886f6e7d53291fae720e737dd', 'rabbitbox_010_bag.20000.tar']]
    #     self.assertEqual(expected, result, "Problem with av, manifest")
    #
    #     # Test for the AIP log.
    #     result = make_aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
    #     expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
    #                  'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
    #                  'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
    #                 ['2025-09-08', 'rabbitbox_010', 'No files deleted', 'Success', 'Success', 'BLANK',
    #                  'Success', 'Success', 'Valid', 'Valid', 'Success', 'Successfully added AIP to manifest',
    #                  'Successfully completed processing']]
    #     self.assertEqual(expected, result, "Problem with AV, AIP log")
    #
    #     # Test for copying to ingest.
    #     # NOTE: this only works when running the test on a Mac, where rsync is available.
    #     result = os.path.exists(os.path.join(os.getcwd(), 'ingest', 'rabbitbox_010_bag.20000.tar'))
    #     self.assertEqual(True, result, "Problem with AV, ingest")
    #
    #     # Test for moving to other location in staging.
    #     result = os.path.exists(os.path.join(aip_staging, 'aips-already-on-ingest-server', 'rabbitbox_010_bag.20000.tar'))
    #     self.assertEqual(True, result, "Problem with AV, staging location")

    def test_bz2(self):
        """Test for an AIP that is tarred and zipped"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        aips_dir = os.getcwd()
        aip_staging = os.path.join(os.getcwd(), 'manifest', 'staging')
        aip = AIP(aips_dir, 'hargrett', None, 'har-ua01', 'folder', 'general', 'har-ua01-001-001', 'title', 1, 'InC', True)
        aip.size = 1000
        aip.log = {'Started': '2025-08-14 11:45:01.000000', 'AIP': 'har-ua01-001-001', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'Valid', 'Package': 'Success',
                   'Manifest': 'n/a', 'Complete': 'n/a'}
        log('header', aips_dir)
        manifest(aip, aip_staging, os.path.join(os.getcwd(), os.path.join(aips_dir, 'ingest')))

        # Test for the manifest.
        manifest_name = f'manifest_tests_hargrett_{datetime.now().strftime("%Y-%m-%d")}.txt'
        result = make_manifest_list(os.path.join(aip_staging, 'aips-ready-to-ingest', manifest_name))
        expected = [['8a88e2fe7d8fa98e978fcbcc59b4e352', 'har-ua01-001-001_bag.1000.tar.bz2']]
        self.assertEqual(expected, result, "Problem with bz2, manifest")

        # Test for the AIP log.
        result = make_aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14', 'har-ua01-001-001', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Valid', 'Success', 'Successfully added AIP to manifest',
                     'Successfully completed processing']]
        self.assertEqual(expected, result, "Problem with bz2, AIP log")

    def test_error_missing(self):
        """Test for when the AIP is not in the expected location"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        aips_dir = os.getcwd()
        aip_staging = os.path.join(os.getcwd(), 'manifest', 'staging')
        aip = AIP(aips_dir, 'hargrett', None, 'har-ua01', 'folder', 'general', 'harg-missing-001', 'title', 1, 'InC', True)
        aip.size = 999
        aip.log = {'Started': '2025-08-14 02:30:01.000000', 'AIP': 'harg-missing-001', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'Valid', 'Package': 'Success',
                   'Manifest': 'n/a', 'Complete': 'n/a'}
        log('header', aips_dir)
        manifest(aip, aip_staging, os.path.join(os.getcwd(), os.path.join(aips_dir, 'ingest')))

        # Test that the manifest was not created.
        manifest_name = f'manifest_tests_hargrett_{datetime.now().strftime("%Y-%m-%d")}.txt'
        result = os.path.exists(os.path.join(aip_staging, 'aips-ready-to-ingest', manifest_name))
        self.assertEqual(result, False, "Problem with error_missing, manifest")

        # Test for the AIP log.
        result = make_aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        aip_path = os.path.join(aip_staging, 'aips-ready-to-ingest', 'harg-missing-001_bag.999.tar.bz2')
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14', 'harg-missing-001', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Valid', 'Success',
                     f"Tar/zip file '{aip_path}' not in aips-ready-for-ingest folder", 'Error during processing']]
        self.assertEqual(expected, result, "Problem with error_missing, AIP log")

    def test_manifest_exists(self):
        """Test for when a manifest already exists and the AIP needs to be added to it"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        # The manifest is made by the test instead of being in the GitHub repo already so the date matches.
        aips_dir = os.getcwd()
        aip_staging = os.path.join(os.getcwd(), 'manifest', 'staging')
        aip = AIP(aips_dir, 'russell', None, 'rbrl-123', 'folder', 'general', 'rbrl-123-er-123456', 'title', 1, 'InC', True)
        aip.size = 300
        aip.log = {'Started': '2025-08-14 02:40:01.000000', 'AIP': 'rbrl-123-er-123456', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'Valid', 'Package': 'Success',
                   'Manifest': 'n/a', 'Complete': 'n/a'}
        log('header', aips_dir)
        manifest_name = f'manifest_tests_russell_{datetime.now().strftime("%Y-%m-%d")}.txt'
        with open(os.path.join(aip_staging, 'aips-ready-to-ingest', manifest_name), 'w', encoding="utf-8") as file:
            file.write('629f0e1886f6e7d53291fae720e737dd  rbrl-123-er-111111_bag.22.tar.bz2\n')
        manifest(aip, aip_staging, os.path.join(os.getcwd(), os.path.join(aips_dir, 'ingest')))

        # Test for the manifest.
        result = make_manifest_list(os.path.join(aip_staging, 'aips-ready-to-ingest', manifest_name))
        expected = [['629f0e1886f6e7d53291fae720e737dd', 'rbrl-123-er-111111_bag.22.tar.bz2'],
                    ['8a88e2fe7d8fa98e978fcbcc59b4e352', 'rbrl-123-er-123456_bag.300.tar.bz2']]
        self.assertEqual(expected, result, "Problem with manifest_exists, manifest")

        # Test for the AIP log.
        result = make_aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14', 'rbrl-123-er-123456', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Valid', 'Success', 'Successfully added AIP to manifest',
                     'Successfully completed processing']]
        self.assertEqual(expected, result, "Problem with manifest_exists, AIP log")

    def test_tar(self):
        """Test for an AIP that is tarred but not zipped"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        aips_dir = os.getcwd()
        aip_staging = os.path.join(os.getcwd(), 'manifest', 'staging')
        aip = AIP(aips_dir, 'magil', None, 'magil-0000', 'folder', 'web', 'magil-seed-2025', 'title', 1, 'InC', False)
        aip.size = 4400
        aip.log = {'Started': '2025-09-08 01:15:01.000000', 'AIP': 'magil-seed-2025', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'Valid', 'Package': 'Success',
                   'Manifest': 'n/a', 'Complete': 'n/a'}
        log('header', aips_dir)
        manifest(aip, aip_staging, os.path.join(os.getcwd(), os.path.join(aips_dir, 'ingest')))

        # Test for the manifest.
        manifest_name = f'manifest_tests_magil_{datetime.now().strftime("%Y-%m-%d")}.txt'
        result = make_manifest_list(os.path.join(aip_staging, 'aips-ready-to-ingest', manifest_name))
        expected = [['629f0e1886f6e7d53291fae720e737dd', 'magil-seed-2025_bag.4400.tar']]
        self.assertEqual(expected, result, "Problem with tar, manifest")

        # Test for the AIP log.
        result = make_aip_log_list(os.path.join(aips_dir, 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-09-08', 'magil-seed-2025', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Valid', 'Success', 'Successfully added AIP to manifest',
                     'Successfully completed processing']]
        self.assertEqual(expected, result, "Problem with tar, AIP log")


if __name__ == "__main__":
    unittest.main()
