"""Testing for the function delete_temp, which takes an AIP class instance as input,
deletes temporary files based on the file names, and logs what was deleted, if anything."""

import datetime
import os
import shutil
import unittest
from scripts.aip_functions import AIP, delete_temp


def make_aip_directory(aip_id):
    """
    Makes a folder for an AIP with test files in the current working directory.
    All have at least two text files and one folder.
    Most have additional files that will be identified as temporary and deleted.
    """
    # Folders and files used in every test.
    os.mkdir(aip_id)
    with open(os.path.join(aip_id, 'Text.txt'), 'w') as file:
        file.write('Test File')
    os.mkdir(os.path.join(aip_id, 'Test Dir'))
    with open(os.path.join(aip_id, 'Test Dir', 'Test Dir Text.txt'), 'w') as file:
        file.write('Test File 2')

    # Temporary files specific to each test.
    # These aren't real temp files, but the filenames are all that need to match to test the script.
    # One file is put in the main AIP folder and another in the Test Dir folder.
    if aip_id == 'ds-store':
        with open(os.path.join(aip_id, '.DS_Store'), 'w') as temp_file:
            temp_file.write('Text')
        with open(os.path.join(aip_id, 'Test Dir', '.DS_Store'), 'w') as temp_file:
            temp_file.write('Text')
    elif aip_id == 'ds-store-2':
        with open(os.path.join(aip_id, '._.DS_Store'), 'w') as temp_file:
            temp_file.write('Text')
        with open(os.path.join(aip_id, 'Test Dir', '._.DS_Store'), 'w') as temp_file:
            temp_file.write('Text')
    elif aip_id == 'thumbs-db':
        with open(os.path.join(aip_id, 'Thumbs.db'), 'w') as temp_file:
            temp_file.write('Text')
        with open(os.path.join(aip_id, 'Test Dir', 'Thumbs.db'), 'w') as temp_file:
            temp_file.write('Text')
    elif aip_id == 'dot-filename':
        with open(os.path.join(aip_id, '.temporary.txt'), 'w') as temp_file:
            temp_file.write('Text')
        with open(os.path.join(aip_id, 'Test Dir', '.temporary.txt'), 'w') as temp_file:
            temp_file.write('Text')
    elif aip_id == 'filename-tmp':
        with open(os.path.join(aip_id, 'temporary.tmp'), 'w') as temp_file:
            temp_file.write('Text')
        with open(os.path.join(aip_id, 'Test Dir', 'temporary.tmp'), 'w') as temp_file:
            temp_file.write('Text')


def aip_directory_print(folder):
    """
    Makes and returns a list with the filepath for every folder and file in an AIP folder.
    This is used to compare the delete_temp function's actual results to the expected results.
    """
    result = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            result.append(os.path.join(root, directory))
        for file in files:
            result.append(os.path.join(root, file))
    return result


class TestDeleteTemp(unittest.TestCase):

    def test_no_temp(self):
        """
        Test for an AIP with no temporary files to delete.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'no-temp', 'no-temp', 'title', 1, True)
        make_aip_directory(aip.id)
        delete_temp(aip)
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join(aip.folder_name, 'Test Dir'),
                    os.path.join(aip.folder_name, 'Text.txt'),
                    os.path.join(aip.folder_name, 'Test Dir', 'Test Dir Text.txt')]
        shutil.rmtree(aip.folder_name)
        self.assertEqual(result, expected, 'Problem with no temporary files')

    def test_ds_store(self):
        """
        Test for an AIP with .DS_Store files to delete.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'ds-store', 'ds-store', 'title', 1, True)
        make_aip_directory(aip.id)
        delete_temp(aip)
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join(aip.folder_name, 'Test Dir'),
                    os.path.join(aip.folder_name, f'{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv'),
                    os.path.join(aip.folder_name, 'Text.txt'),
                    os.path.join(aip.folder_name, 'Test Dir', 'Test Dir Text.txt')]
        shutil.rmtree(aip.folder_name)
        self.assertEqual(result, expected, 'Problem with deleting .DS_Store')

    def test_ds_store_2(self):
        """
        Test for an AIP with ._.DS_Store files to delete.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'ds-store-2', 'ds-store-2', 'title', 1, True)
        make_aip_directory(aip.id)
        delete_temp(aip)
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join(aip.folder_name, 'Test Dir'),
                    os.path.join(aip.folder_name, f'{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv'),
                    os.path.join(aip.folder_name, 'Text.txt'),
                    os.path.join(aip.folder_name, 'Test Dir', 'Test Dir Text.txt')]
        shutil.rmtree(aip.folder_name)
        self.assertEqual(result, expected, 'Problem with deleting ._.DS_Store')

    def test_thumbs_db(self):
        """
        Test for an AIP with Thumbs.db files to delete.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'thumbs-db', 'thumbs-db', 'title', 1, True)
        make_aip_directory(aip.id)
        delete_temp(aip)
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join(aip.folder_name, 'Test Dir'),
                    os.path.join(aip.folder_name, 'Text.txt'),
                    os.path.join(aip.folder_name, f'{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv'),
                    os.path.join(aip.folder_name, 'Test Dir', 'Test Dir Text.txt')]
        shutil.rmtree(aip.folder_name)
        self.assertEqual(result, expected, 'Problem with deleting Thumbs.db')

    def test_dot_prefix(self):
        """
        Test for an AIP with .filename files to delete.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'dot-filename', 'dot-filename', 'title', 1, True)
        make_aip_directory(aip.id)
        delete_temp(aip)
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join(aip.folder_name, 'Test Dir'),
                    os.path.join(aip.folder_name, f'{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv'),
                    os.path.join(aip.folder_name, 'Text.txt'),
                    os.path.join(aip.folder_name, 'Test Dir', 'Test Dir Text.txt')]
        shutil.rmtree(aip.folder_name)
        self.assertEqual(result, expected, 'Problem with deleting files with dot prefix')

    def test_tmp_extension(self):
        """
        Test for an AIP with filename.tmp files to delete.
        """
        aip = AIP(os.getcwd(), 'test', 'coll-1', 'filename-tmp', 'filename-tmp', 'title', 1, True)
        make_aip_directory(aip.id)
        delete_temp(aip)
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join(aip.folder_name, 'Test Dir'),
                    os.path.join(aip.folder_name, f'{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv'),
                    os.path.join(aip.folder_name, 'Text.txt'),
                    os.path.join(aip.folder_name, 'Test Dir', 'Test Dir Text.txt')]
        shutil.rmtree(aip.folder_name)
        self.assertEqual(result, expected, 'Problem with deleting .tmp extension')


if __name__ == '__main__':
    unittest.main()
