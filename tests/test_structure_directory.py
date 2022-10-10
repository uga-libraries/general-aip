"""Testing for the function structure_directory, which takes an AIP class instance as input and
organizes the contents of the AIP folder into metadata and objects subfolders.
There is error handling for if a folder named objects or metadata already exists.
There are a few files that are sorted into metadata and everthing else goes into objects."""

import os
import unittest
from scripts.aip_functions import structure_directory


class TestStructureDirectory(unittest.TestCase):

    def setUp(self):
        """
        Make the AIP class instances and corresponding directories needed for the tests.
        """

    def test_error_objects_exists(self):
        """
        Test for structuring an AIP when there is already an objects subfolder and no metadata subfolder.
        This is an error that the script can handle.
        """

    def test_error_both_exist(self):
        """
        Test for structuring an AIP when there are already objects and metadata subfolders.
        This is an error that the script can handle.
        """

    def test_error_metadata_exists(self):
        """
        Test for structuring an AIP with there is already a metadata subfolder and no objects subfolder.
        This is an error that the script can handle.
        """

    def test_sort_files_deleted(self):
        """
        Test for structuring an AIP which contains a deletion log, which goes in the metadata subfolder.
        All other files will go to the objects subfolder.
        """

    def test_sort_emory(self):
        """
        Test for structuring an AIP which contains an Emory metadata file, which goes in the metadata subfolder.
        All other files will go in the objects subfolder.
        """

    def test_no_metadata(self):
        """
        Test for structuring an AIP with no metadata files. All files will go in the objects subfolder.
        """


if __name__ == '__main__':
    unittest.main()
