"""Testing for the function structure_directory, which takes an AIP class instance as input and
organizes the contents of the AIP folder into metadata and objects subfolders.
There is error handling for if a folder named objects or metadata already exists.
There are a few files that are sorted into metadata and everything else goes into objects."""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, log, structure_directory


def aip_dir_make(aip_id):
    """
    Makes a folder for an AIP with test files.
    All have at least three text files and one folder.
    Some have additional files and folders needed for their test.
    """
    # Folders and files used in every test.
    os.mkdir(aip_id)
    os.mkdir(os.path.join(aip_id, 'Test Dir'))
    with open(os.path.join(aip_id, 'Text.txt'), 'w') as file:
        file.write('Test File')
    with open(os.path.join(aip_id, 'Text2.txt'), 'w') as file:
        file.write('Test File 2')
    with open(os.path.join(aip_id, 'Test Dir', 'Text3.txt'), 'w') as file:
        file.write('Test File 3')

    # Folders and files used for a specific test.
    if aip_id == 'err-objects':
        os.mkdir(os.path.join(aip_id, 'objects'))
        with open(os.path.join(aip_id, 'objects', 'Text4.txt'), 'w') as file:
            file.write('Test File 4')
    elif aip_id == 'err-both':
        os.mkdir(os.path.join(aip_id, 'objects'))
        with open(os.path.join(aip_id, 'objects', 'Text4.txt'), 'w') as file:
            file.write('Test File 4')
        os.mkdir(os.path.join(aip_id, 'metadata'))
        with open(os.path.join(aip_id, 'metadata', 'Text5.txt'), 'w') as file:
            file.write('Test File 5')
    elif aip_id == 'err-metadata':
        os.mkdir(os.path.join(aip_id, 'metadata'))
        with open(os.path.join(aip_id, 'metadata', 'Text5.txt'), 'w') as file:
            file.write('Test File 5')
    elif aip_id == 'sort-log':
        with open(os.path.join(aip_id, 'sort-log_files-deleted_2022-10-31_del.csv'), 'w') as file:
            file.write('Deletion Log Test File')
    elif aip_id == 'sort-emory':
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

    def tearDown(self):
        """
        Deletes the log and error folder, if any, for a clean start to the next test.
        """
        os.remove('..\\aip_log.csv')
        if os.path.exists('..\\errors'):
            shutil.rmtree('..\\errors')

    def test_error_objects_exists(self):
        """
        Test for structuring an AIP when there is already an objects subfolder and no metadata subfolder.
        This is an error that the script can handle.
        """
        objects_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-objects', 'err-objects', 'title', 1, True)
        aip_dir_make('err-objects')
        structure_directory(objects_aip)
        result = aip_dir_print('..\\errors\\objects_folder_exists\\err-objects')
        expected = ['..\\errors\\objects_folder_exists\\err-objects\\objects',
                    '..\\errors\\objects_folder_exists\\err-objects\\Test Dir',
                    '..\\errors\\objects_folder_exists\\err-objects\\Text.txt',
                    '..\\errors\\objects_folder_exists\\err-objects\\Text2.txt',
                    '..\\errors\\objects_folder_exists\\err-objects\\objects\\Text4.txt',
                    '..\\errors\\objects_folder_exists\\err-objects\\Test Dir\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with error - objects exists')

    def test_error_both_exist(self):
        """
        Test for structuring an AIP when there are already objects and metadata subfolders.
        This is an error that the script can handle.
        """
        both_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-both', 'err-both', 'title', 1, True)
        aip_dir_make('err-both')
        structure_directory(both_aip)
        result = aip_dir_print('..\\errors\\objects_folder_exists\\err-both')
        expected = ['..\\errors\\objects_folder_exists\\err-both\\metadata',
                    '..\\errors\\objects_folder_exists\\err-both\\objects',
                    '..\\errors\\objects_folder_exists\\err-both\\Test Dir',
                    '..\\errors\\objects_folder_exists\\err-both\\Text.txt',
                    '..\\errors\\objects_folder_exists\\err-both\\Text2.txt',
                    '..\\errors\\objects_folder_exists\\err-both\\metadata\\Text5.txt',
                    '..\\errors\\objects_folder_exists\\err-both\\objects\\Text4.txt',
                    '..\\errors\\objects_folder_exists\\err-both\\Test Dir\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with error - metadata and objects exists')

    def test_error_metadata_exists(self):
        """
        Test for structuring an AIP with there is already a metadata subfolder and no objects subfolder.
        This is an error that the script can handle.
        """
        metadata_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-metadata', 'err-metadata', 'title', 1, True)
        aip_dir_make('err-metadata')
        structure_directory(metadata_aip)
        result = aip_dir_print('..\\errors\\metadata_folder_exists\\err-metadata')
        expected = ['..\\errors\\metadata_folder_exists\\err-metadata\\metadata',
                    '..\\errors\\metadata_folder_exists\\err-metadata\\objects',
                    '..\\errors\\metadata_folder_exists\\err-metadata\\Test Dir',
                    '..\\errors\\metadata_folder_exists\\err-metadata\\Text.txt',
                    '..\\errors\\metadata_folder_exists\\err-metadata\\Text2.txt',
                    '..\\errors\\metadata_folder_exists\\err-metadata\\metadata\\Text5.txt',
                    '..\\errors\\metadata_folder_exists\\err-metadata\\Test Dir\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with error - metadata exists')

    def test_sort_files_deleted(self):
        """
        Test for structuring an AIP which contains a deletion log, which goes in the metadata subfolder.
        All other files will go to the objects subfolder.
        """
        log_aip = AIP(os.getcwd(), 'test', 'coll-1', 'sort-log', 'sort-log', 'title', 1, True)
        aip_dir_make('sort-log')
        structure_directory(log_aip)
        result = aip_dir_print(log_aip.folder_name)
        shutil.rmtree('sort-log')
        expected = ['sort-log\\metadata', 'sort-log\\objects', 'sort-log\\metadata\\sort-log_files-deleted_2022-10-31_del.csv',
                    'sort-log\\objects\\Test Dir', 'sort-log\\objects\\Text.txt',
                    'sort-log\\objects\\Text2.txt', 'sort-log\\objects\\Test Dir\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with sort deletion log')

    def test_sort_emory(self):
        """
        Test for structuring an AIP which contains an Emory metadata file, which goes in the metadata subfolder.
        All other files will go in the objects subfolder.
        """
        emory_aip = AIP(os.getcwd(), 'emory', 'coll-1', 'sort-emory', 'sort-emory', 'title', 1, True)
        aip_dir_make('sort-emory')
        structure_directory(emory_aip)
        result = aip_dir_print(emory_aip.folder_name)
        shutil.rmtree('sort-emory')
        expected = ['sort-emory\\metadata', 'sort-emory\\objects', 'sort-emory\\metadata\\EmoryMD_Test.txt',
                    'sort-emory\\objects\\Test Dir', 'sort-emory\\objects\\Text.txt',
                    'sort-emory\\objects\\Text2.txt', 'sort-emory\\objects\\Test Dir\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with sort Emory metadata')

    def test_sort_none(self):
        """
        Test for structuring an AIP with no metadata files. All files will go in the objects subfolder.
        """
        none_aip = AIP(os.getcwd(), 'test', 'coll-1', 'sort-none', 'sort-none', 'title', 1, True)
        aip_dir_make('sort-none')
        structure_directory(none_aip)
        result = aip_dir_print(none_aip.folder_name)
        shutil.rmtree('sort-none')
        expected = ['sort-none\\metadata', 'sort-none\\objects', 'sort-none\\objects\\Test Dir',
                    'sort-none\\objects\\Text.txt', 'sort-none\\objects\\Text2.txt', 'sort-none\\objects\\Test Dir\\Text3.txt']
        self.assertEqual(result, expected, 'Problem with sort no metadata')


if __name__ == '__main__':
    unittest.main()
