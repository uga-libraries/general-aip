"""Testing for the function bag, which takes an AIP class instance as input and makes it into a bag,
with md5 and sha256 checksums. The bag folder is renamed with '_bag' suffix and the bag is validated.
There is error handling for if the bag is not valid.
There are two functions for bagging, one to make it and one to validate it."""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, log, make_bag, validate_bag


class TestBag(unittest.TestCase):

    def setUp(self):
        """
        Makes an AIP and corresponding folder to use for testing.
        To save time, since they are not used for the test, the metadata files are text files and not real.
        """
        self.aip = AIP(os.getcwd(), 'test', 'coll-1', 'aip-folder', 'aip-id', 'title', 1, True)
        os.mkdir(self.aip.id)
        os.mkdir(os.path.join(self.aip.id, 'metadata'))
        with open(os.path.join(self.aip.id, 'metadata', 'file_fits.xml'), 'w') as file:
            file.write("Text")
        with open(os.path.join(self.aip.id, 'metadata', f'{self.aip.id}_preservation.xml'), 'w') as file:
            file.write("Text")
        os.mkdir(os.path.join(self.aip.id, 'objects'))
        with open(os.path.join(self.aip.id, 'objects', 'file.txt'), 'w') as file:
            file.write("Test")

    def tearDown(self):
        """
        Deletes the test AIP, regardless of if it was correctly renamed to add '_bag' or not.
        """
        if os.path.exists(f'{self.aip.id}_bag'):
            shutil.rmtree(f'{self.aip.id}_bag')
        else:
            shutil(self.aip.id)

    def test_make_bag(self):
        """
        Test for making a bag of an AIP folder.
        There are no input variations or error handling to test.
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
