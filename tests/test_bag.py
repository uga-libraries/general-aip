"""Testing for the function bag, which takes an AIP class instance as input and makes it into a bag,
with md5 and sha256 checksums. The bag folder is renamed with '_bag' suffix and the bag is validated.
There is error handling for if the bag is not valid.
There are two functions for bagging, one to make it and one to validate it."""

import datetime
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
        Test for making a bag of an AIP folder.
        The bag directory structure is used to test the result.
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

    def test_valid_bag(self):
        """
        Test for validating a valid bag.
        The AIP log is used to test the result.
        """
        make_bag(self.aip)
        validate_bag(self.aip)
        result = self.aip.log["BagValid"]
        expected = f'Bag valid on {datetime.date.today()}'
        # Since the log for bagging includes a timestamp, assert cannot require an exact match.
        self.assertIn(expected, result, 'Problem with validating a valid bag')

    def test_not_valid_bag(self):
        """
        Test for validating a bag that is not valid.
        The validation log, which will be in the errors folder, is used to test the result.
        NOTE: bagit will also print validation result to the terminal in red.
        """
        make_bag(self.aip)

        # Replacing the MD5 manifest with incorrect information so the bag is no longer valid.
        # Fixity is changed for file.txt, which also changes the fixity of manifest-md5.txt.
        # If the files are changed instead, it produces a one-line payload error, which doesn't test log formatting.
        with open(os.path.join(f'{self.aip.id}_bag', 'manifest-md5.txt'), 'w') as file:
            file.write('9dffbf69ffba8bc38bc4e01abf4b1675  data/metadata/aip-id_preservation.xml\n')
            file.write('9dffbf69ffba8bc38bc4e01abf4b1675  data/metadata/file_fits.xml\n')
            file.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  data/objects/file.txt')
        validate_bag(self.aip)

        # If the validation log is present, the contents of the log are the test result.
        # The contents are sorted because bagit saves the errors in an inconsistent order.
        # Otherwise, default error language is the result.
        log_path = os.path.join('..', 'errors', 'bag_not_valid', 'aip-id_bag_validation.txt')
        if os.path.exists(log_path):
            with open(log_path, 'r') as file:
                result = file.readlines()
                result.sort()
        else:
            result = 'The validation log was not found'
        expected = ['data\\objects\\file.txt md5 validation failed: expected="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" found="0cbc6611f5540bd0809a388dc95a615b"\n',
                    'manifest-md5.txt md5 validation failed: expected="ca30eea54d30b25cca192fb4a38efbc3" found="7fd32d6a82c9ba59534103d4a877e3d8"\n',
                    'manifest-md5.txt sha256 validation failed: expected="ce73cc2e81ad3cc1b9f24d84a57984b96a4322914f7b02067a11c81b739ae548" found="0752123baadbf461f459b56be3c91b84548582d6ef6f4497f5ee6c528afdca10"\n']

        self.assertEqual(result, expected, 'Problem with validating a bag that is not valid')


if __name__ == '__main__':
    unittest.main()
