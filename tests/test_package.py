"""Testing for the function package, which tars and (optionally) zips the bag for the AIP,
renames it to add the unzipped size, and saves to the aips-ready-to-ingest folder.

NOTE: The packaged AIPs have a different size depending on if the tests were run on Windows or Mac,
so the expected results and the tearDown look for either possible size.
"""

import os
import tarfile
import unittest
from aip_functions import AIP, log, package
from test_validate_bag import aip_log_list


class TestPackage(unittest.TestCase):

    def tearDown(self):
        """Deletes the AIP log and packaged AIP if created"""
        log_path = os.path.join(os.getcwd(), 'package', 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        aips_ready_path = os.path.join(os.getcwd(), 'staging', 'aips-ready-to-ingest')
        for pkg in ['test-aip-1_bag.663.tar', 'test-aip-1_bag.663.tar.bz2',
                    'test-aip-1_bag.673.tar', 'test-aip-1_bag.673.tar.bz2']:
            if os.path.exists(os.path.join(aips_ready_path, pkg)):
                os.remove(os.path.join(aips_ready_path, pkg))

    def test_tar_zip(self):
        """Test for an AIP that should be tarred and zipped."""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'package')
        aip_staging = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'test', None, 'collection', 'folder', 'general', 'test-aip-1', 'title', 1, True)
        package(aip, aip_staging)

        # Test that the tar.bz2 file is in the aips-to-ingest folder.
        result = (os.path.exists(os.path.join(aip_staging, 'aips-ready-to-ingest', 'test-aip-1_bag.663.tar.bz2')) or
                  os.path.exists(os.path.join(aip_staging, 'aips-ready-to-ingest', 'test-aip-1_bag.673.tar.bz2')))
        self.assertEqual(result, True, "Problem with tar_zip, aips-ready-to-ingest")
        
        # Test that the AIP size is updated.
        result = aip.size
        expected = [663, 673]
        self.assertIn(result, expected, "Problem with tar_zip, AIP size")

        # Test that the AIP log is updated.
        result = aip.log['Package']
        expected = 'Successfully made package'
        self.assertEqual(expected, result, "Problem with tar_zip, AIP log")

    def test_tar(self):
        """Test for an AIP that should be tarred but not zipped"""
        # Makes the test input and runs the function.
        aips_dir = os.path.join(os.getcwd(), 'package')
        aip_staging = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'test', None, 'collection', 'folder', 'general', 'test-aip-1', 'title', 1, False)
        package(aip, aip_staging)

        # Test that the tar file is in the aips-to-ingest folder.
        result = (os.path.exists(os.path.join(aip_staging, 'aips-ready-to-ingest', 'test-aip-1_bag.663.tar')) or
                  os.path.exists(os.path.join(aip_staging, 'aips-ready-to-ingest', 'test-aip-1_bag.673.tar')))
        self.assertEqual(result, True, "Problem with tar, aips-ready-to-ingest")

        # Test that the tar file contains the expected file paths.
        # Catches errors in how the tar is constructed, like if it contains unnecessary folders.
        try:
            with tarfile.open(os.path.join(aip_staging, 'aips-ready-to-ingest', 'test-aip-1_bag.663.tar')) as tar:
                result = tar.getnames()
        except FileNotFoundError:
            with tarfile.open(os.path.join(aip_staging, 'aips-ready-to-ingest', 'test-aip-1_bag.673.tar')) as tar:
                result = tar.getnames()
        result.sort()
        # Windows includes bag name in path and Mac has "." instead.
        # Mac also has a copy of every file and folder with "._" prefix, which seems to be from the tar command.
        # The bag is still valid and does now show any of these in the manifest.
        expected = [['.', './._bag-info.txt', './._bagit.txt', './._data', './._manifest-md5.txt',
                     './._tagmanifest-md5.txt', './bag-info.txt', './bagit.txt', './data', './data/._metadata',
                     './data/._objects', './data/metadata', './data/metadata/._Placeholder for metadata.txt',
                     './data/metadata/Placeholder for metadata.txt', './data/objects',
                     './data/objects/._Placeholder for content.txt', './data/objects/Placeholder for content.txt',
                     './manifest-md5.txt', './tagmanifest-md5.txt', '._.'],
                    ['test-aip-1_bag', 'test-aip-1_bag/bag-info.txt', 'test-aip-1_bag/bagit.txt', 'test-aip-1_bag/data',
                     'test-aip-1_bag/data/metadata', 'test-aip-1_bag/data/metadata/Placeholder for metadata.txt',
                     'test-aip-1_bag/data/objects', 'test-aip-1_bag/data/objects/Placeholder for content.txt',
                     'test-aip-1_bag/manifest-md5.txt', 'test-aip-1_bag/tagmanifest-md5.txt']]
        self.assertIn(result, expected, "Problem with tar, tar contents")

        # Test that the AIP size is updated.
        result = aip.size
        expected = [663, 673]
        self.assertIn(result, expected, "Problem with tar, AIP size")

        # Test that the AIP log is updated.
        result = aip.log['Package']
        expected = 'Successfully made package'
        self.assertEqual(expected, result, "Problem with tar, AIP log")

    def test_error(self):
        """Test for when the bag folder to be packaged is missing"""
        # Makes the test input and runs the function.
        # The AIP log is updated as if previous steps have run correctly.
        aips_dir = os.path.join(os.getcwd(), 'package')
        aip_staging = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'test', None, 'collection', 'folder', 'general', 'test-missing-1', 'title', 1, False)
        aip.log = {'Started': '2025-08-14 10:55AM', 'AIP': 'test-missing-1', 'Deletions': 'No files deleted',
                   'ObjectsError': 'Success', 'MetadataError': 'Success', 'FITSTool': 'None', 'FITSError': 'Success',
                   'PresXML': 'Success', 'PresValid': 'Valid', 'BagValid': 'Valid', 'Package': 'n/a',
                   'Manifest': 'n/a', 'Complete': 'n/a'}
        log('header', aips_dir)
        package(aip, aip_staging)

        # Test for the AIP log.
        result = aip_log_list(os.path.join(os.getcwd(), 'package', 'aip_log.csv'))
        expected = [['Time Started', 'AIP ID', 'Files Deleted', 'Objects Folder', 'Metadata Folder',
                     'FITS Tool Errors', 'FITS Combination Errors', 'Preservation.xml Made', 'Preservation.xml Valid',
                     'Bag Valid', 'Package Errors', 'Manifest Errors', 'Processing Complete'],
                    ['2025-08-14 10:55AM', 'test-missing-1', 'No files deleted', 'Success', 'Success', 'BLANK',
                     'Success', 'Success', 'Valid', 'Valid',
                     f'Could not tar. Bag not in expected location: {os.path.join(aips_dir, "test-missing-1_bag")}',
                     'BLANK', 'Error during processing']]
        self.assertEqual(expected, result, "Problem with error")


if __name__ == "__main__":
    unittest.main()
