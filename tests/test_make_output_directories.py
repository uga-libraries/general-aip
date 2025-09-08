"""Testing for the function make_output_directories, which makes directories for output in staging 
if they don't already exist. Different directories are made depending on the mode.

The function check_configuration() confirms that staging is a valid path, so no test is needed for that error.
"""

import os
import shutil
import unittest
from aip_functions import make_output_directories


def directory_print(path):
    """Makes a list of folders within the directory to compare to expected results"""
    folder_list = []
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            folder_list.append(os.path.join(root, dir_name))
    folder_list.sort()
    return folder_list


class TestMakeOutputDirectories(unittest.TestCase):

    def tearDown(self):
        """Deletes the finished staging folder (copy of data made for each test)"""
        staging_folders = ['staging_av_all', 'staging_av_none', 'staging_av_partial',
                           'staging_all', 'staging_none', 'staging_partial']
        for staging_folder in staging_folders:
            staging_path = os.path.join(os.getcwd(), 'make_output_directories', staging_folder)
            if os.path.exists(staging_path):
                shutil.rmtree(staging_path)

    def test_av_all(self):
        """Test for av mode when all the folders already exist"""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_av_all')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'av')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = [os.path.join(staging, 'aips-already-on-ingest-server'),
                    os.path.join(staging, 'aips-ready-to-ingest'),
                    os.path.join(staging, 'fits-xmls'),
                    os.path.join(staging, 'md5-manifests-for-aips'),
                    os.path.join(staging, 'mediainfo-xmls'),
                    os.path.join(staging, 'mediainfo-xmls', 'mediainfo-raw-output'),
                    os.path.join(staging, 'mediainfo-xmls', 'pbcore2-xml'),
                    os.path.join(staging, 'movs-to-bag'),
                    os.path.join(staging, 'preservation-xmls')]
        self.assertEqual(expected, result, "Problem with av_all")

    def test_av_none(self):
        """Test for av mode when none of the folders already exist"""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_av_none')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'av')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = [os.path.join(staging, 'aips-already-on-ingest-server'),
                    os.path.join(staging, 'aips-ready-to-ingest'),
                    os.path.join(staging, 'fits-xmls'),
                    os.path.join(staging, 'md5-manifests-for-aips'),
                    os.path.join(staging, 'mediainfo-xmls'),
                    os.path.join(staging, 'mediainfo-xmls', 'mediainfo-raw-output'),
                    os.path.join(staging, 'mediainfo-xmls', 'pbcore2-xml'),
                    os.path.join(staging, 'movs-to-bag'),
                    os.path.join(staging, 'preservation-xmls')]
        self.assertEqual(expected, result, "Problem with av_none")

    def test_av_partial(self):
        """Test for av mode when some of the folders already exist"""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_av_partial')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'av')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = [os.path.join(staging, 'aips-already-on-ingest-server'),
                    os.path.join(staging, 'aips-ready-to-ingest'),
                    os.path.join(staging, 'fits-xmls'),
                    os.path.join(staging, 'md5-manifests-for-aips'),
                    os.path.join(staging, 'mediainfo-xmls'),
                    os.path.join(staging, 'mediainfo-xmls', 'mediainfo-raw-output'),
                    os.path.join(staging, 'mediainfo-xmls', 'pbcore2-xml'),
                    os.path.join(staging, 'movs-to-bag'),
                    os.path.join(staging, 'preservation-xmls')]
        self.assertEqual(expected, result, "Problem with av_partial")

    def test_non_av_all(self):
        """Test for mode other than av when all the folders already exist"""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_all')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'non_av')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        self.assertEqual(expected, result, "Problem with non_av_all")

    def test_non_av_none(self):
        """Test for mode other than av when none of the folders already exist"""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_none')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'non_av')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        self.assertEqual(expected, result, "Problem with non_av_none")

    def test_non_av_partial(self):
        """Test for mode other than av when some the three folders already exist."""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_partial')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'non_av')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        self.assertEqual(expected, result, "Problem with non_av_partial")


if __name__ == "__main__":
    unittest.main()
