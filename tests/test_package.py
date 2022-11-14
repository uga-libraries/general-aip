"""Testing for the function package, which tars and (optionally) zips the bag for the AIP,
renames it to add the unzipped size, and saves to the aips-to-ingest folder.

The function currently tests for the operating system and uses different commands.
This test is just for Windows. The function will be updated to use Python instead of OS-specific tools."""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, make_output_directories, make_bag, package


class TestPackage(unittest.TestCase):

    def setUp(self):
        """
        Makes an AIP instance, corresponding bagged folder with files, and the script output folders.
        The folder does not have the required metadata, since that isn't necessary for this test.
        """
        self.aip = AIP(os.getcwd(), 'test', 'test-coll', 'test-aip-id', 'test-aip-id', 'title', 1, to_zip=True)
        os.mkdir(self.aip.folder_name)
        for file_name in ('file1.txt', 'file2.txt', 'file3.txt'):
            with open(os.path.join(self.aip.folder_name, file_name), 'w') as file:
                file.write('Test Test Test Test' * 100)
        make_bag(self.aip)
        make_output_directories()

    def tearDown(self):
        """
        Deletes the script output folders and bagged AIP.
        """
        shutil.rmtree(f'{self.aip.id}_bag')
        shutil.rmtree(os.path.join('..', 'aips-to-ingest'))
        os.rmdir(os.path.join('..', 'fits-xml'))
        os.rmdir(os.path.join('..', 'preservation-xml'))

    def test_tar_zip(self):
        """
        Test for an AIP that should be tarred and zipped.
        Result for testing is if the tarred/zipped file is in the aips-to-ingest folder.
        """
        package(self.aip)
        result = os.path.exists(os.path.join('..', 'aips-to-ingest', 'test-aip-id_bag.6791.tar.bz2'))
        self.assertEqual(result, True, 'Problem with tar and zip')

    def test_tar(self):
        """
        Test for an AIP that should be tarred and not zipped.
        Result for testing is if the tarred file is in the aips-to-ingest folder.
        """
        self.aip.to_zip=False
        package(self.aip)
        result = os.path.exists(os.path.join('..', 'aips-to-ingest', 'test-aip-id_bag.6791.tar'))
        self.assertEqual(result, True, 'Problem with tar')


if __name__ == '__main__':
    unittest.main()
