"""Testing for the function make_bag, which takes an AIP class instance as input and makes it into a bag,
with md5 and sha256 checksums. The bag folder is renamed with "_bag" suffix."""

from datetime import datetime
import os
import shutil
import unittest
from aip_functions import AIP, make_bag


def make_bag_list(bag_path):
    """Make a list of all files within the bag to compare against the expected results"""
    bag_list = []
    for root, dirs, files in os.walk(bag_path):
        for file in files:
            bag_list.append(os.path.join(root, file))
    return bag_list


class TestMakeBag(unittest.TestCase):

    def tearDown(self):
        """If they are present, deletes the test AIPs if correctly renamed to add "_bag" or not"""
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aips = ['rabbitbox_0001', 'rbrl_025_er_000001', 'rbrl025_0001_media']
        for aip in aips:
            if os.path.exists(os.path.join(aips_dir, aip)):
                shutil.rmtree(os.path.join(aips_dir, aip))
            elif os.path.exists(os.path.join(aips_dir, f'{aip}_bag')):
                shutil.rmtree(os.path.join(aips_dir, f'{aip}_bag'))

    def test_av_bmac(self):
        """Test for making a bag out of an AIP folder that is AV from BMAC"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aip = AIP(aips_dir, 'bmac', 'mp4', 'rabbitbox', 'folder', 'av', 'rabbitbox_0001', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_copy'), os.path.join(aips_dir, aip.id))
        make_bag(aip)

        # Verifies the AIP is now a bag, based on the folder name and contents.
        result = make_bag_list(os.path.join(aips_dir, f'{aip.id}_bag'))
        date = datetime.today().strftime('%Y-%#m-%#d')
        expected = [os.path.join(aips_dir, f'{aip.id}_bag', 'bag-info.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'bagit.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', 'Placeholder for AIP content.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', f'{aip.id}_files-deleted_{date}_del.csv')]
        self.assertEqual(result, expected, "Problem with av_bmac")

    def test_av_russell(self):
        """Test for making a bag out of an AIP folder that is AV from Russell"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aip = AIP(aips_dir, 'russell', 'mp4', 'rbrl025', 'folder', 'av', 'rbrl025_0001_media', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_copy'), os.path.join(aips_dir, aip.id))
        make_bag(aip)

        # Verifies the AIP is now a bag, based on the folder name and contents.
        result = make_bag_list(os.path.join(aips_dir, f'{aip.id}_bag'))
        expected = [os.path.join(aips_dir, f'{aip.id}_bag', 'bag-info.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'bagit.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-sha256.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-sha256.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', 'Placeholder for AIP content.txt')]
        self.assertEqual(result, expected, "Problem with av_russell")

    def test_general(self):
        """Test for making a bag out of an AIP folder that is the general type"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aip = AIP(aips_dir, 'russell', None, 'rbrl_025', 'folder', 'general', 'rbrl_025_er_000001', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_copy'), os.path.join(aips_dir, aip.id))
        make_bag(aip)

        # Verifies the AIP is now a bag, based on the folder name and contents.
        result = make_bag_list(os.path.join(aips_dir, f'{aip.id}_bag'))
        expected = [os.path.join(aips_dir, f'{aip.id}_bag', 'bag-info.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'bagit.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-sha256.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-sha256.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', 'Placeholder for AIP content.txt')]
        self.assertEqual(result, expected, "Problem with general")


if __name__ == "__main__":
    unittest.main()
