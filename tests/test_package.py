"""Testing for the function package, which tars and (optionally) zips the bag for the AIP,
renames it to add the unzipped size, and saves to the aips-to-ingest folder.

The function currently tests for the operating system and uses different commands.
This test is just for Windows. The function will be updated to use Python instead of OS-specific tools."""

import os
import shutil
import unittest
from aip_functions import AIP, make_output_directories, make_bag, package


class TestPackage(unittest.TestCase):

    def setUp(self):
        """
        Makes an AIP instance, corresponding bagged folder with files, and the script output folders.
        The folder does not have the required metadata, since that isn"t necessary for this test.
        """
        self.aip = AIP(os.getcwd(), "test", "test-coll", "test-aip-id", "test-aip-id", "title", 1, to_zip=True)
        os.mkdir(self.aip.folder_name)
        for file_name in ("file1.txt", "file2.txt", "file3.txt"):
            with open(os.path.join(self.aip.folder_name, file_name), "w") as file:
                file.write("Test Test Test Test" * 100)
        make_bag(self.aip)
        make_output_directories()

    def tearDown(self):
        """
        Deletes the bagged AIP, script output folders, and AIP log (if created).
        """
        shutil.rmtree(f"{self.aip.id}_bag")
        shutil.rmtree(os.path.join("..", "aips-to-ingest"))
        os.rmdir(os.path.join("..", "fits-xml"))
        os.rmdir(os.path.join("..", "preservation-xml"))

        if os.path.exists(os.path.join("..", "aip_log.csv")):
            os.remove(os.path.join("..", "aip_log.csv"))

    def test_tar_zip(self):
        """
        Test for an AIP that should be tarred and zipped.
        """
        # Runs the function being tested.
        package(self.aip)

        # Test that the tar.bz2 file is in the aips-to-ingest folder.
        result_ingest = os.path.exists(os.path.join("..", "aips-to-ingest", "test-aip-id_bag.6791.tar.bz2"))
        self.assertEqual(result_ingest, True, "Problem with tar and zip, aips-to-ingest")
        
        # Test that the tar.bz2 file and tar file are not in the AIPs directory.
        # The tar.bz2 file should have been moved to aips-to-ingest
        # and the tar file is temporary and should have been deleted.
        result_aip_dir = (os.path.exists("test-aip-id_bag.6791.tar"), os.path.exists("test-aip-id_bag.6791.tar.bz2"))
        expected_aip_dir = (False, False)
        self.assertEqual(result_aip_dir, expected_aip_dir, "Problem with tar and zip, AIPs directory")

        # Test for the AIP log.
        result_log = self.aip.log["Package"]
        expected_log = "Successfully made package"
        self.assertEqual(result_log, expected_log, "Problem with tar/zip, log")

    def test_tar(self):
        """
        Test for an AIP that should be tarred and not zipped.
        Result for testing is if the tarred file is in the aips-to-ingest folder, plus the AIP log.
        """
        # Updates the default to_zip value to not zip and runs the function being tested.
        self.aip.to_zip = False
        package(self.aip)

        # Test that the tar file is in the aips-to-ingest folder.
        result_ingest = os.path.exists(os.path.join("..", "aips-to-ingest", "test-aip-id_bag.6791.tar"))
        self.assertEqual(result_ingest, True, "Problem with tar, aips-to-ingest")

        # Test that the tar file is not in the AIPs directory. It should have been moved to aips-to-ingest.
        result_aip_dir = os.path.exists("test-aip=id_bag.6791.tar")
        self.assertEqual(result_aip_dir, False, "Problem with tar, AIPs directory")

        # Test for the AIP log.
        result_log = self.aip.log["Package"]
        expected_log = "Successfully made package"
        self.assertEqual(result_log, expected_log, "Problem with tar, log")

    def test_tar_error(self):
        """
        Test error handling if 7zip is not able to tar the file.
        """
        # Updates the default directory to a directory that does not exist, to cause the error,
        # and runs the function being tested.
        self.aip.directory = "DoesNotExist"
        package(self.aip)

        # Test for the AIP log, Package.
        result_package = self.aip.log["Package"]
        expected_package = "Could not tar. 7zip error: \r\n" \
                           "WARNING: The system cannot find the file specified.\r\n" \
                           "DoesNotExist\r\n\r\n"
        self.assertEqual(result_package, expected_package, "Problem with tar error, log: Package")

        # Test for the AIP log, Complete.
        result_complete = self.aip.log["Complete"]
        expected_complete = "Error during processing"
        self.assertEqual(result_complete, expected_complete, "Problem with tar error, log: complete")


if __name__ == "__main__":
    unittest.main()
