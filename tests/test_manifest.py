"""Testing for the function manifest, which takes an AIP class instance as input,
calculates the MD5 for the tar.bz2 version of the AIP, and adds that to the manifest.
There is error handling for if the .tar.bz2 version of the AIP doesn't exist and
for errors from the tool which generates the MD5.

In the production script, the manifest is made or edited after each AIP is made.
For faster testing, this makes the output of the previous steps (a tar and/or zip file in aips-to-ingest),
instead of using the functions to do that.
Also for faster testing, the tar and/or zip file is a text file with the '.tar' or '.tar.bz2' extensions.
The tests only require that the file name be correct.

NOTE: was not able to make a test for md5deep error handling.
The only way to cause an error is give it an incorrect path, but that is caught at an earlier step.
We plan to stop using md5deep fairly soon, so leaving that without a test.
"""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, log, make_output_directories, manifest


class TestManifest(unittest.TestCase):

    def setUp(self):
        """
        Starts the log and makes the script output folders, which are typically done in the main body of the script.
        """
        log('header')
        make_output_directories()

    def tearDown(self):
        """
        Deletes the log and script output folders for a clean start to the next test.
        """
        os.remove(os.path.join('..', 'aip_log.csv'))
        shutil.rmtree(os.path.join('..', 'aips-to-ingest'))
        shutil.rmtree(os.path.join('..', 'fits-xml'))
        shutil.rmtree(os.path.join('..', 'preservation-xml'))

    def test_one_tar(self):
        """
        Test for adding a single tar file to the manifest.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'one-tar-folder', 'one-tar', 'title', 1, to_zip=False)
        aip.size = 4000
        with open(os.path.join('..', 'aips-to-ingest', f'{aip.id}_bag.4000.tar'), 'w') as fake_file:
            fake_file.write("Test")
        manifest(aip)
        with open(os.path.join('..', 'aips-to-ingest', 'manifest_test.txt'), 'r') as file:
            result = file.read()
        expected = '0cbc6611f5540bd0809a388dc95a615b  one-tar_bag.4000.tar\n'
        self.assertEqual(expected, result, 'Problem with one tar')

    def test_one_zip(self):
        """
        Test for adding a single tarred and zipped file to the manifest.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'one-zip-folder', 'one-zip', 'title', 1, to_zip=True)
        aip.size = 4000
        with open(os.path.join('..', 'aips-to-ingest', f'{aip.id}_bag.4000.tar.bz2'), 'w') as fake_file:
            fake_file.write("Test")
        manifest(aip)
        with open(os.path.join('..', 'aips-to-ingest', 'manifest_test.txt'), 'r') as file:
            result = file.read()
        expected = '0cbc6611f5540bd0809a388dc95a615b  one-zip_bag.4000.tar.bz2\n'
        self.assertEqual(expected, result, 'Problem with one zip')

    def test_multiple_departments(self):
        """
        Test for adding files from multiple departments to the manifest.
        """
        # Makes 1 aip for department bmac and 2 aips for department test.
        for aip in ('aip1', 'aip2', 'aip3'):
            department = 'test'
            if aip == 'aip2':
                department = 'bmac'
            aip = AIP(os.getcwd(), department, 'coll', f'{aip}-folder', aip, 'title', 1, to_zip=True)
            aip.size = 4000
            with open(os.path.join('..', 'aips-to-ingest', f'{aip.id}_bag.4000.tar.bz2'), 'w') as fake_file:
                fake_file.write("Test")
            manifest(aip)

        # Reads both of the manifests and combines the data into a single variable.
        # Compares that to the expected results.
        with open(os.path.join('..', 'aips-to-ingest', 'manifest_bmac.txt'), 'r') as file:
            bmac = file.read()
        with open(os.path.join('..', 'aips-to-ingest', 'manifest_test.txt'), 'r') as file:
            test = file.read()
        result = bmac + test
        expected = '0cbc6611f5540bd0809a388dc95a615b  aip2_bag.4000.tar.bz2\n' \
                   '0cbc6611f5540bd0809a388dc95a615b  aip1_bag.4000.tar.bz2\n' \
                   '0cbc6611f5540bd0809a388dc95a615b  aip3_bag.4000.tar.bz2\n'
        self.assertEqual(expected, result, 'Problem with multiple departments')

    def test_one_missing_error_handling(self):
        """
        Test for error handling of a tarred file missing from aips-to-ingest.
        The tar for another AIP is present, so the manifest is made.
        """
        # Makes two AIP instances but only makes the tar file for the first AIP.
        aip1 = AIP(os.getcwd(), 'test', 'coll-1', 'aip1-folder', 'aip1', 'title', 1, to_zip=False)
        aip1.size = 4000
        with open(os.path.join('..', 'aips-to-ingest', f'{aip1.id}_bag.4000.tar'), 'w') as fake_file:
            fake_file.write("Test")
        manifest(aip1)
        aip2 = AIP(os.getcwd(), 'test', 'coll-1', 'aip2-folder', 'aip2', 'title', 1, to_zip=False)
        manifest(aip2)

        with open(os.path.join('..', 'aips-to-ingest', 'manifest_test.txt'), 'r') as file:
            result = file.read()
        expected = '0cbc6611f5540bd0809a388dc95a615b  aip1_bag.4000.tar\n'
        self.assertEqual(expected, result, 'Problem with one missing error handling')

    def test_all_missing_error_handling(self):
        """
        Test for error handling of a tarred file missing from aips-to-ingest.
        There are no other AIPs, so the manifest is not made. The log is used for testing.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'aip-folder', 'aip', 'title', 1, to_zip=False)
        manifest(aip)
        result = aip.log["Package"]
        expected = 'Tar/zip file not in aips-to-ingest folder.'
        self.assertEqual(expected, result, 'Problem with all missing error handling')


if __name__ == '__main__':
    unittest.main()
