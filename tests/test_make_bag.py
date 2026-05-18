"""Testing for the function make_bag, which takes an AIP class instance as input and makes it into a bag,
with md5 and sha256 checksums. The bag folder is renamed with "_bag" suffix."""

from datetime import datetime
import os
import shutil
import unittest
from aip_functions import AIP, make_bag
from test_script import make_directory_list


class TestMakeBag(unittest.TestCase):

    def tearDown(self):
        """If they are present, deletes the test AIPs if correctly renamed to add "_bag" or not"""
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aips = ['rabbitbox_0001', 'rbrl_025_er_000001', 'rbrl025_0001_media', 'test_001_01']
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
        result = make_directory_list(os.path.join(aips_dir, f'{aip.id}_bag'))
        date = datetime.today().strftime('%Y-%#m-%#d')
        expected = [os.path.join(aips_dir, f'{aip.id}_bag', 'bag-info.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'bagit.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', 'Placeholder for AIP content.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-md5.txt')]
        self.assertEqual(expected, result, "Problem with av_bmac")

    def test_av_russell(self):
        """Test for making a bag out of an AIP folder that is AV from Russell"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aip = AIP(aips_dir, 'russell', 'mp4', 'rbrl025', 'folder', 'av', 'rbrl025_0001_media', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_copy'), os.path.join(aips_dir, aip.id))
        make_bag(aip)

        # Verifies the AIP is now a bag, based on the folder name and contents.
        result = make_directory_list(os.path.join(aips_dir, f'{aip.id}_bag'))
        expected = [os.path.join(aips_dir, f'{aip.id}_bag', 'bag-info.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'bagit.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', 'Placeholder for AIP content.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-sha256.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-sha256.txt')]
        self.assertEqual(expected, result, "Problem with av_russell")

    def test_general(self):
        """Test for making a bag out of an AIP folder that is the general type"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aip = AIP(aips_dir, 'russell', None, 'rbrl_025', 'folder', 'general', 'rbrl_025_er_000001', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_copy'), os.path.join(aips_dir, aip.id))
        make_bag(aip)

        # Verifies the AIP is now a bag, based on the folder name and contents.
        result = make_directory_list(os.path.join(aips_dir, f'{aip.id}_bag'))
        expected = [os.path.join(aips_dir, f'{aip.id}_bag', 'bag-info.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'bagit.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', 'Placeholder for AIP content.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-sha256.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-sha256.txt')]
        self.assertEqual(expected, result, "Problem with general")

    def test_temp(self):
        """Test for making a bag out of an AIP folder that has temp files that should be deleted"""
        # Makes the test input and runs the function.
        # A copy of the AIP is made since this test should move it to an error folder.
        aips_dir = os.path.join(os.getcwd(), 'make_bag')
        aip = AIP(aips_dir, 'test', None, 'test_001', 'folder', 'general', 'test_001_01', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, f'{aip.id}_copy'), os.path.join(aips_dir, aip.id))
        make_bag(aip)

        # Verifies the AIP is now a bag, based on the folder name and contents, with none of the temp files.
        result = make_directory_list(os.path.join(aips_dir, f'{aip.id}_bag'))
        expected = [os.path.join(aips_dir, f'{aip.id}_bag', 'bag-info.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'bagit.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'data', 'Placeholder for AIP content.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'manifest-sha256.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-md5.txt'),
                    os.path.join(aips_dir, f'{aip.id}_bag', 'tagmanifest-sha256.txt')]
        self.assertEqual(expected, result, "Problem with temp")


if __name__ == "__main__":
    unittest.main()
