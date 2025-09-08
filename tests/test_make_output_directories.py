"""Testing for the function make_output_directories, which creates three directories in the current directory.
It does not have any inputs and returns nothing.

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
        """Deletes the staging folder (copy of data made for each test)"""
        staging_folders = ['staging_av_all', 'staging_av_none', 'staging_av_partial',
                           'staging_general_all', 'staging_general_none', 'staging_general_partial']
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

    def test_general_all(self):
        """Test for general mode when all three folders already exist"""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_general_all')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'general')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        self.assertEqual(expected, result, "Problem with general_all")

    def test_general_none(self):
        """Test for general mode when none of the three folders already exist"""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_general_none')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'general')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        self.assertEqual(expected, result, "Problem with general_none")

    def test_general_partial(self):
        """Test for general mode when one of the three folders (aips-ready-to-ingest) already exists."""
        # Makes a copy of the test input and runs the function.
        staging = os.path.join(os.getcwd(), 'make_output_directories', 'staging_general_partial')
        shutil.copytree(f'{staging}_copy', staging)
        make_output_directories(staging, 'general')

        # Verifies that staging has the expected folders.
        result = directory_print(staging)
        expected = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
        self.assertEqual(expected, result, "Problem with general_partial")


if __name__ == "__main__":
    unittest.main()
