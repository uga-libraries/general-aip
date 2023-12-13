"""Testing for the function manifest, which takes an AIP class instance as input,
calculates the MD5 for the tar.bz2 version of the AIP, and adds that to the manifest.
There is error handling for if the .tar.bz2 version of the AIP doesn"t exist and
for errors from the tool which generates the MD5.

In the production script, the manifest is made or edited after each AIP is made.
For faster testing, this makes the output of the previous steps (a tar and/or zip file in aips-to-ingest),
instead of using the functions to do that.
Also for faster testing, the tar and/or zip file is a text file with the ".tar" or ".tar.bz2" extensions.
The tests only require that the file name be correct.

NOTE: was not able to make a test for md5deep error handling.
The only way to cause an error is give it an incorrect path, but that is caught at an earlier step.
We plan to stop using md5deep fairly soon, so leaving that without a test.
"""

import os
import pandas as pd
import shutil
import unittest
from aip_functions import AIP, log, make_output_directories, manifest


def manifest_to_list(path):
    """
    Reads the manifest and returns a list of lists, where each list is a row in the manifest.
    """
    df = pd.read_csv(path, delim_whitespace=True)
    row_list = [df.columns.to_list()] + df.values.tolist()
    return row_list


class TestManifest(unittest.TestCase):

    def setUp(self):
        """
        Makes the script output folders.
        """
        make_output_directories()

    def tearDown(self):
        """
        Deletes the log and script output folders.
        """
        os.remove(os.path.join("..", "aip_log.csv"))
        shutil.rmtree(os.path.join("..", "aips-to-ingest"))
        shutil.rmtree(os.path.join("..", "fits-xml"))
        shutil.rmtree(os.path.join("..", "preservation-xml"))

    def test_one_tar(self):
        """
        Test for adding a single tar file to the manifest.
        Result for testing is the contents of the manifest plus the AIP log.
        """
        # Makes 1 AIP instance, an AIP tar placeholder, and the manifest.
        aip = AIP(os.getcwd(), "test", "coll-1", "one-tar-folder", "one-tar", "title", 1, to_zip=False)
        aip.size = 4000
        with open(os.path.join("..", "aips-to-ingest", f"{aip.id}_bag.4000.tar"), "w") as fake_file:
            fake_file.write("Test")
        manifest(aip)

        # Test for the manifest.
        result = manifest_to_list(os.path.join("..", "aips-to-ingest", "manifest_test.txt"))
        expected = [["0cbc6611f5540bd0809a388dc95a615b", "one-tar_bag.4000.tar"]]
        self.assertEqual(expected, result, "Problem with one tar, manifest")

        # Test for the AIP log: Manifest.
        result_log = aip.log["Manifest"]
        expected_log = "Successfully added AIP to manifest"
        self.assertEqual(result_log, expected_log, "Problem with one tar, log: Manifest")

        # Test for the AIP log: Complete.
        result_log2 = aip.log["Complete"]
        expected_log2 = "Successfully completed processing"
        self.assertEqual(result_log2, expected_log2, "Problem with one tar, log: Complete")

    def test_one_zip(self):
        """
        Test for adding a single tarred and zipped file to the manifest.
        Result for testing is the contents of the manifest plus the AIP log.
        """
        # Makes 1 AIP instance, an AIP tar.bz2 placeholder, and the manifest.
        aip = AIP(os.getcwd(), "test", "coll-1", "one-zip-folder", "one-zip", "title", 1, to_zip=True)
        aip.size = 4000
        with open(os.path.join("..", "aips-to-ingest", f"{aip.id}_bag.4000.tar.bz2"), "w") as fake_file:
            fake_file.write("Test")
        manifest(aip)

        # Test for the manifest.
        result = manifest_to_list(os.path.join("..", "aips-to-ingest", "manifest_test.txt"))
        expected = [["0cbc6611f5540bd0809a388dc95a615b", "one-zip_bag.4000.tar.bz2"]]
        self.assertEqual(expected, result, "Problem with one zip, manifest")

        # Test for the AIP log: Manifest.
        result_log = aip.log["Manifest"]
        expected_log = "Successfully added AIP to manifest"
        self.assertEqual(result_log, expected_log, "Problem with one zip, log: Manifest")

        # Test for the AIP log: Complete.
        result_log2 = aip.log["Complete"]
        expected_log2 = "Successfully completed processing"
        self.assertEqual(result_log2, expected_log2, "Problem with one zip, log: Complete")

    def test_multiple_departments(self):
        """
        Test for adding files from multiple departments to the manifest.
        Result for testing is the contents of the manifest plus the AIP log.
        """
        # Makes 1 AIP instance for department bmac and 2 for department test.
        aip1 = AIP(os.getcwd(), "test", "coll", "aip1-folder", "aip1", "title", 1, to_zip=True)
        aip2 = AIP(os.getcwd(), "bmac", "coll", "aip2-folder", "aip2", "title", 1, to_zip=True)
        aip3 = AIP(os.getcwd(), "test", "coll", "aip3-folder", "aip3", "title", 1, to_zip=True)

        # Makes an AIP tar.bz2 placeholder for all three of the AIP instances and makes the manifest.
        for aip in (aip1, aip2, aip3):
            aip.size = 4000
            with open(os.path.join("..", "aips-to-ingest", f"{aip.id}_bag.4000.tar.bz2"), "w") as fake_file:
                fake_file.write("Test")
            manifest(aip)

        # Test for the bmac manifest.
        result_bmac = manifest_to_list(os.path.join("..", "aips-to-ingest", "manifest_bmac.txt"))
        expected_bmac = [["0cbc6611f5540bd0809a388dc95a615b", "aip2_bag.4000.tar.bz2"]]
        self.assertEqual(result_bmac, expected_bmac, "Problem with multiple depts: bmac, manifest")

        # Test for the bmac AIP log: Manifest.
        result_bmac_log = aip2.log["Manifest"]
        expected_bmac_log = "Successfully added AIP to manifest"
        self.assertEqual(result_bmac_log, expected_bmac_log, "Problem with multiple depts: bmac, log: Manifest")

        # Test for the bmac AIP log: Complete.
        result_bmac_log2 = aip2.log["Complete"]
        expected_bmac_log2 = "Successfully completed processing"
        self.assertEqual(result_bmac_log2, expected_bmac_log2, "Problem with multiple depts: bmac, log: Complete")

        # Test for the test manifest.
        result_test = manifest_to_list(os.path.join("..", "aips-to-ingest", "manifest_test.txt"))
        expected_test = [["0cbc6611f5540bd0809a388dc95a615b", "aip1_bag.4000.tar.bz2"],
                         ["0cbc6611f5540bd0809a388dc95a615b", "aip3_bag.4000.tar.bz2"]]
        self.assertEqual(result_test, expected_test, "Problem with multiple depts: test, manifest")

        # Test for the test AIP log: Manifest.
        result_test_log = (aip1.log["Manifest"], aip3.log["Manifest"])
        expected_test_log = ("Successfully added AIP to manifest", "Successfully added AIP to manifest")
        self.assertEqual(result_test_log, expected_test_log, "Problem with multiple depts: test, log: Manifest")

        # Test for the test AIP log: Complete.
        result_test_log2 = (aip1.log["Complete"], aip3.log["Complete"])
        expected_test_log2 = ("Successfully completed processing", "Successfully completed processing")
        self.assertEqual(result_test_log2, expected_test_log2, "Problem with multiple depts: test, log: Complete")

    def test_error_one_missing(self):
        """
        Test for error handling of a tarred file missing from aips-to-ingest.
        The tar for another AIP is present, so the manifest is made.
        """
        # Makes two AIP instances for department test.
        aip1 = AIP(os.getcwd(), "test", "coll-1", "aip1-folder", "aip1", "title", 1, to_zip=False)
        aip2 = AIP(os.getcwd(), "test", "coll-1", "aip2-folder", "aip2", "title", 1, to_zip=False)

        # Only makes an AIP tar placeholder for one AIP instance and makes the manifest for both.
        aip1.size = 4000
        with open(os.path.join("..", "aips-to-ingest", f"{aip1.id}_bag.4000.tar"), "w") as fake_file:
            fake_file.write("Test")
        manifest(aip1)
        manifest(aip2)

        # Test for the manifest.
        result = manifest_to_list(os.path.join("..", "aips-to-ingest", "manifest_test.txt"))
        expected = [["0cbc6611f5540bd0809a388dc95a615b", "aip1_bag.4000.tar"]]
        self.assertEqual(result, expected, "Problem with error: one missing, manifest")

        # Test for the AIP log: Manifest.
        result_log = (aip1.log["Manifest"], aip2.log["Manifest"])
        expected_log = ("Successfully added AIP to manifest", "Tar/zip file not in aips-to-ingest folder")
        self.assertEqual(result_log, expected_log, "Problem with error: one missing, log: Manifest")

        # Test for the AIP log: Complete.
        result_log2 = (aip1.log["Complete"], aip2.log["Complete"])
        expected_log2 = ("Successfully completed processing", "Error during processing")
        self.assertEqual(result_log2, expected_log2, "Problem with error: one missing, log: Complete")

    def test_error_all_missing(self):
        """
        Test for error handling of a tarred file missing from aips-to-ingest.
        There are no other AIPs, so the manifest is not made.
        """
        # Makes two AIP instances for department test.
        aip1 = AIP(os.getcwd(), "test", "coll-1", "aip1-folder", "aip1", "title", 1, to_zip=False)
        aip2 = AIP(os.getcwd(), "test", "coll-1", "aip2-folder", "aip2", "title", 1, to_zip=False)

        # Does not make an AIP tar placeholder for either AIP instance and makes the manifest for both.
        manifest(aip1)
        manifest(aip2)

        # Test for the manifest not being made.
        result = os.path.exists(os.path.join("..", "aips-to-ingest", "manifest_test.txt"))
        self.assertEqual(result, False, "Problem with error: all missing, manifest")

        # Test for the AIP log: Manifest.
        result_log = (aip1.log["Manifest"], aip2.log["Manifest"])
        expected_log = ("Tar/zip file not in aips-to-ingest folder", "Tar/zip file not in aips-to-ingest folder")
        self.assertEqual(result_log, expected_log, "Problem with error: all missing, log: Manifest")

        # Test for the AIP log: Complete.
        result_log2 = (aip1.log["Complete"], aip2.log["Complete"])
        expected_log2 = ("Error during processing", "Error during processing")
        self.assertEqual(result_log2, expected_log2, "Problem with error: all missing, log: Complete")


if __name__ == "__main__":
    unittest.main()
