"""Testing for the function structure_directory, which takes an AIP class instance as input and
organizes the contents of the AIP folder into metadata and objects subfolders.
There is error handling for if a folder named objects or metadata already exists in the AIP folder.
There are a few files that are sorted into metadata and everything else goes into objects."""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, log, structure_directory


def aip_dir_make(aip_id):
    """
    Makes a folder for an AIP with test files in the current working directory.
    All have at least three text files and one folder.
    Some have additional files and folders needed for their test.
    """
    # Folders and files used in every test.
    os.mkdir(aip_id)
    os.mkdir(os.path.join(aip_id, 'Test Dir'))
    with open(os.path.join(aip_id, 'Text.txt'), 'w') as file:
        file.write('Test File')
    with open(os.path.join(aip_id, 'Text 2.txt'), 'w') as file:
        file.write('Test File 2')
    with open(os.path.join(aip_id, 'Test Dir', 'Test Dir Text.txt'), 'w') as file:
        file.write('Test File 3')

    # Folders and files used for a specific test.
    if aip_id == 'err-objects':
        os.mkdir(os.path.join(aip_id, 'objects'))
        with open(os.path.join(aip_id, 'objects', 'Objects Text.txt'), 'w') as file:
            file.write('Test File 4')
    elif aip_id == 'err-both':
        os.mkdir(os.path.join(aip_id, 'objects'))
        with open(os.path.join(aip_id, 'objects', 'Objects Text.txt'), 'w') as file:
            file.write('Test File 4')
        os.mkdir(os.path.join(aip_id, 'metadata'))
        with open(os.path.join(aip_id, 'metadata', 'Metadata Text.txt'), 'w') as file:
            file.write('Test File 5')
    elif aip_id == 'err-metadata':
        os.mkdir(os.path.join(aip_id, 'metadata'))
        with open(os.path.join(aip_id, 'metadata', 'Metadata Text.txt'), 'w') as file:
            file.write('Test File 5')
    elif aip_id == 'sort-log':
        with open(os.path.join(aip_id, 'sort-log_files-deleted_2022-10-31_del.csv'), 'w') as file:
            file.write('Deletion Log Test File')
    elif aip_id == 'sort-emory':
        with open(os.path.join(aip_id, 'EmoryMD_Test.txt'), 'w') as file:
            file.write('Emory Metadata Test File')


def aip_dir_print(folder):
    """
    Makes and returns a list with the filepath for every folder and file in an AIP folder.
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
        os.remove(os.path.join('..', 'aip_log.csv'))
        if os.path.exists(os.path.join('..', 'errors')):
            shutil.rmtree(os.path.join('..', 'errors'))

    def test_error_objects_exists(self):
        """
        Test for structuring an AIP when there is already an objects subfolder and no metadata subfolder.
        This is an error that the script can handle.
        """
        objects_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-objects', 'err-objects', 'title', 1, True)
        aip_dir_make('err-objects')
        structure_directory(objects_aip)
        aip_path = os.path.join('..', 'errors', 'objects_folder_exists', 'err-objects')
        result = aip_dir_print(aip_path)
        expected = [os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with error - objects exists')

    def test_error_both_exist(self):
        """
        Test for structuring an AIP when there are already objects and metadata subfolders.
        This is an error that the script can handle.
        """
        both_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-both', 'err-both', 'title', 1, True)
        aip_dir_make('err-both')
        structure_directory(both_aip)
        aip_path = os.path.join('..', 'errors', 'objects_folder_exists', 'err-both')
        result = aip_dir_print(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with error - metadata and objects exists')

    def test_error_metadata_exists(self):
        """
        Test for structuring an AIP when there is already a metadata subfolder and no objects subfolder.
        This is an error that the script can handle.
        """
        metadata_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-metadata', 'err-metadata', 'title', 1, True)
        aip_dir_make('err-metadata')
        structure_directory(metadata_aip)
        aip_path = os.path.join('..', 'errors', 'metadata_folder_exists', 'err-metadata')
        result = aip_dir_print(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
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
        expected = [os.path.join('sort-log', 'metadata'),
                    os.path.join('sort-log', 'objects'),
                    os.path.join('sort-log', 'metadata', 'sort-log_files-deleted_2022-10-31_del.csv'),
                    os.path.join('sort-log', 'objects', 'Test Dir'),
                    os.path.join('sort-log', 'objects', 'Text 2.txt'),
                    os.path.join('sort-log', 'objects', 'Text.txt'),
                    os.path.join('sort-log', 'objects', 'Test Dir', 'Test Dir Text.txt')]
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
        expected = [os.path.join('sort-emory', 'metadata'),
                    os.path.join('sort-emory', 'objects'),
                    os.path.join('sort-emory', 'metadata', 'EmoryMD_Test.txt'),
                    os.path.join('sort-emory', 'objects', 'Test Dir'),
                    os.path.join('sort-emory', 'objects', 'Text 2.txt'),
                    os.path.join('sort-emory', 'objects', 'Text.txt'),
                    os.path.join('sort-emory', 'objects', 'Test Dir', 'Test Dir Text.txt')]
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
        expected = [os.path.join('sort-none', 'metadata'),
                    os.path.join('sort-none', 'objects'),
                    os.path.join('sort-none', 'objects', 'Test Dir'),
                    os.path.join('sort-none', 'objects', 'Text 2.txt'),
                    os.path.join('sort-none', 'objects', 'Text.txt'),
                    os.path.join('sort-none', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with sort no metadata')


if __name__ == '__main__':
    unittest.main()
