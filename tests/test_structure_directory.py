"""Testing for the function structure_directory, which takes an AIP class instance as input and
organizes the contents of the AIP folder into metadata and objects subfolders.
There is error handling for if a folder named objects or metadata already exists.
There are a few files that are sorted into metadata and everthing else goes into objects."""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, log, move_error, structure_directory


def aip_dir_make(aip_id):
    """
    Makes a folder for an AIP with test files.
    All have at least three text files and one folder.
    Some have additional files and folders needed for their test.
    """
    # Folders and files used in every test.
    os.mkdir(aip_id)
    os.mkdir(os.path.join(aip_id, 'Test 1'))
    with open(os.path.join(aip_id, 'Text.txt'), 'w') as file:
        file.write('Test File')
    with open(os.path.join(aip_id, 'Text2.txt'), 'w') as file:
        file.write('Test File 2')
    with open(os.path.join(aip_id, 'Test 1', 'Text3.txt'), 'w') as file:
        file.write('Test File 3')

    # Folders and files used for a specific test.
    if aip_id == 'sort-log':
        with open(os.path.join(aip_id, 'sort-log_files-deleted_2022-10-31_del.csv'), 'w') as file:
            file.write('Deletion Log Test File')
    elif aip_id == 'sort-em':
        with open(os.path.join(aip_id, 'EmoryMD_Test.txt'), 'w') as file:
            file.write('Emory Metadata Test File')


def aip_dir_print(folder):
    """
    Makes and returns a list with the filepath for every folder and file in an AIP's directory.
    This is used to compare the structure_directory function's actual results to the expected results.
    """
    result = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            result.append(os.path.join(root, directory))
        for file in files:
            result.append(os.path.join(root, file))
    return result


class TestStructureDirectory(unittest.TestCase):

    def setUp(self):
        """
        Starts the log, which is typically done in the main body of the script.
        """
        log('header')

    # def test_error_objects_exists(self):
    #     """
    #     Test for structuring an AIP when there is already an objects subfolder and no metadata subfolder.
    #     This is an error that the script can handle.
    #     """
    #
    # def test_error_both_exist(self):
    #     """
    #     Test for structuring an AIP when there are already objects and metadata subfolders.
    #     This is an error that the script can handle.
    #     """
    #
    # def test_error_metadata_exists(self):
    #     """
    #     Test for structuring an AIP with there is already a metadata subfolder and no objects subfolder.
    #     This is an error that the script can handle.
    #     """
    #
    def test_sort_files_deleted(self):
        """
        Test for structuring an AIP which contains a deletion log, which goes in the metadata subfolder.
        All other files will go to the objects subfolder.
        """
        log_aip = AIP(os.getcwd(), 'test', 'coll-1', 'sort-log', 'sort-log', 'title', 1, True)
        aip_dir_make(log_aip.folder_name)
        structure_directory(log_aip)
        result = aip_dir_print(log_aip.folder_name)
        shutil.rmtree('sort-log')
        expected = ['sort-log\\metadata', 'sort-log\\objects', 'sort-log\\metadata\\sort-log_files-deleted_2022-10-31_del.csv',
                    'sort-log\\objects\\Test 1', 'sort-log\\objects\\Text.txt',
                    'sort-log\\objects\\Text2.txt', 'sort-log\\objects\\Test 1\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with sort no metadata')

    def test_sort_emory(self):
        """
        Test for structuring an AIP which contains an Emory metadata file, which goes in the metadata subfolder.
        All other files will go in the objects subfolder.
        """
        emory_aip = AIP(os.getcwd(), 'emory', 'coll-1', 'sort-em', 'sort-em', 'title', 1, True)
        aip_dir_make(emory_aip.folder_name)
        structure_directory(emory_aip)
        result = aip_dir_print(emory_aip.folder_name)
        shutil.rmtree('sort-em')
        expected = ['sort-em\\metadata', 'sort-em\\objects', 'sort-em\\metadata\\EmoryMD_Test.txt',
                    'sort-em\\objects\\Test 1', 'sort-em\\objects\\Text.txt',
                    'sort-em\\objects\\Text2.txt', 'sort-em\\objects\\Test 1\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with sort no metadata')

    def test_sort_none(self):
        """
        Test for structuring an AIP with no metadata files. All files will go in the objects subfolder.
        """
        none_aip = AIP(os.getcwd(), 'test', 'coll-1', 'sort-none', 'sort-none', 'title', 1, True)
        aip_dir_make(none_aip.folder_name)
        structure_directory(none_aip)
        result = aip_dir_print(none_aip.folder_name)
        shutil.rmtree('sort-none')
        expected = ['sort-none\\metadata', 'sort-none\\objects', 'sort-none\\objects\\Test 1',
                    'sort-none\\objects\\Text.txt', 'sort-none\\objects\\Text2.txt', 'sort-none\\objects\\Test 1\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with sort no metadata')


if __name__ == '__main__':
    unittest.main()
