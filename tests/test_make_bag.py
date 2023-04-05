"""Testing for the function make_bag, which takes an AIP class instance as input and makes it into a bag,
with md5 and sha256 checksums. The bag folder is renamed with '_bag' suffix."""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, make_bag


class TestBag(unittest.TestCase):

    def setUp(self):
        """
        Makes an AIP instance and corresponding folder to use for testing.
        """
        # Makes the AIP instance and a folder named with the AIP ID.
        self.aip = AIP(os.getcwd(), 'test', 'coll-1', 'aip-folder', 'aip-id', 'title', 1, True)
        os.mkdir(self.aip.id)

        # Makes the AIP metadata folder and metadata files.
        # To save time, since they are not used for the test, the metadata files are text files and not real.
        os.mkdir(os.path.join(self.aip.id, 'metadata'))
        with open(os.path.join(self.aip.id, 'metadata', 'file_fits.xml'), 'w') as file:
            file.write("Text")
        with open(os.path.join(self.aip.id, 'metadata', f'{self.aip.id}_preservation.xml'), 'w') as file:
            file.write("Text")

        # Makes the AIP object folder and a test file.
        os.mkdir(os.path.join(self.aip.id, 'objects'))
        with open(os.path.join(self.aip.id, 'objects', 'file.txt'), 'w') as file:
            file.write("Test")

    def tearDown(self):
        """
        If they are present, deletes the test AIP (if correctly renamed to add '_bag' or if it isn't),
        the AIP log and the errors folder.
        """
        if os.path.exists(f'{self.aip.id}_bag'):
            shutil.rmtree(f'{self.aip.id}_bag')
        elif os.path.exists(self.aip.id):
            shutil.rmtree(self.aip.id)

        log_path = os.path.join('..', 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        errors_path = os.path.join('..', 'errors')
        if os.path.exists(errors_path):
            shutil.rmtree(errors_path)

    def test_make_bag(self):
        """
        Test for making a bag out of an AIP folder.
        Result for testing is the contents of the bag folder (the bag metadata files).
        """
        make_bag(self.aip)

        # If the renamed bag folder is present, a directory print of the folder is the test result.
        # Otherwise, default error language is the result.
        if os.path.exists(f'{self.aip.id}_bag'):
            result = []
            for item in os.listdir(f'{self.aip.id}_bag'):
                result.append(item)
        else:
            result = "AIP's bag folder not found"

        expected = ['bag-info.txt', 'bagit.txt', 'data', 'manifest-md5.txt', 'manifest-sha256.txt',
                    'tagmanifest-md5.txt', 'tagmanifest-sha256.txt']

        self.assertEqual(result, expected, 'Problem with make bag')


if __name__ == '__main__':
    unittest.main()
