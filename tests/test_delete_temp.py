"""Testing for the function delete_temp, which takes an AIP class instance as input,
deletes temporary files based on the file names, and logs what was deleted, if anything.

There are two separate unit tests for each type of temporary file,
one that tests the file is deleted and the AIP log is updated correctly and
one that tests that the files deleted log is made correctly."""

from datetime import date
import os
import pandas as pd
import shutil
import unittest
from aip_functions import AIP, delete_temp


def aip_directory_print(folder):
    """
    Makes and returns a list with the filepath for every folder and file in an AIP folder.
    This is used to test that only the expected file is deleted from the AIP folder.
    """
    result = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            result.append(os.path.join(root, directory))
        for file in files:
            result.append(os.path.join(root, file))
    return result


def deletion_log_rows(log_path):
    """
    Makes and returns a list with the contents of each row in the deletion log.
    The time in the Date Last Modified is removed, leaving just the date, so it is predictable for comparison.
    This is used to test that the correct information was saved to the log.
    """
    df = pd.read_csv(log_path)
    df['Date Last Modified'] = df['Date Last Modified'].str.split(' ').str[0]
    row_list = [df.columns.to_list()] + df.values.tolist()
    return row_list


class TestDeleteTemp(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the AIP folders created by each test.
        """
        aip_folders = ['aip-id_dot', 'aip-id_ds-store', 'aip-id_ds-store-2', 'aip-id_tmp', 'aip-id_thumbs']
        for aip_folder in aip_folders:
            aip_path = os.path.join(os.getcwd(), 'delete_temp', aip_folder)
            if os.path.exists(aip_path):
                shutil.rmtree(aip_path)

    def test_no_temp(self):
        """
        Test for an AIP with no temporary files to delete.
        """
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id', 'title', 1, True)
        delete_temp(aip)

        # Test for the AIP folder.
        aip_path = os.path.join(aips_dir, aip.id)
        result = aip_directory_print(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with test for no temporary files, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log['Deletions']
        expected_aip_log = 'No files deleted'
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for no temporary files, AIP log")

    def test_ds_store(self):
        """
        Test for an AIP with .DS_Store files to delete.
        """
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_ds-store_copy'), os.path.join(aips_dir, 'aip-id_ds-store'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_ds-store', 'title', 1, True)
        delete_temp(aip)

        # Variables used throughout the test: the path to the deletion log and today's date formatted YYYY-MM-DD.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%#m-%#d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = aip_directory_print(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    deletion_log,
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with test for .DS_Store, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log['Deletions']
        expected_aip_log = 'File(s) deleted'
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for .DS_Store, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                            [os.path.join(aips_dir, 'aip-id_ds-store', '.DS_Store'), '.DS_Store', 0, today],
                            [os.path.join(aips_dir, 'aip-id_ds-store', 'Test Dir', '.DS_Store'), '.DS_Store', 0, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for .DS_Store, deletion log")

    def test_ds_store_2(self):
        """
        Test for an AIP with ._.DS_Store files to delete.
        """
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_ds-store-2_copy'), os.path.join(aips_dir, 'aip-id_ds-store-2'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_ds-store-2', 'title', 1, True)
        delete_temp(aip)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%#m-%#d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = aip_directory_print(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    deletion_log,
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with test for ._.DS_Store, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log['Deletions']
        expected_aip_log = 'File(s) deleted'
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for ._.DS_Store, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                            [os.path.join(aips_dir, 'aip-id_ds-store-2', '._.DS_Store'), '._.DS_Store', 0, today],
                            [os.path.join(aips_dir, 'aip-id_ds-store-2', 'Test Dir', '._.DS_Store'),
                             '._.DS_Store', 0, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for .DS_Store, deletion log")

    def test_thumbs_db(self):
        """
        Test for an AIP with Thumbs.db files to delete.
        """
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_thumbs_copy'), os.path.join(aips_dir, 'aip-id_thumbs'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_thumbs', 'title', 1, True)
        delete_temp(aip)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%#m-%#d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = aip_directory_print(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    deletion_log,
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with test for Thumbs.db, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log['Deletions']
        expected_aip_log = 'File(s) deleted'
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for Thumbs.db, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                            [os.path.join(aips_dir, 'aip-id_thumbs', 'Thumbs.db'), 'Thumbs.db', 25, today],
                            [os.path.join(aips_dir, 'aip-id_thumbs', 'Test Dir', 'Thumbs.db'),
                             'Thumbs.db', 2590, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for Thumbs.db, deletion log")

    def test_dot_prefix(self):
        """
        Test for an AIP with .filename files to delete.
        """
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_dot_copy'), os.path.join(aips_dir, 'aip-id_dot'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_dot', 'title', 1, True)
        delete_temp(aip)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%#m-%#d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = aip_directory_print(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    deletion_log,
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with test for dot prefix, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log['Deletions']
        expected_aip_log = 'File(s) deleted'
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for dot prefix, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                            [os.path.join(aips_dir, 'aip-id_dot', '.temp.txt'), '.temp.txt', 0, today],
                            [os.path.join(aips_dir, 'aip-id_dot', 'Test Dir', '.temp.txt'), '.temp.txt', 0, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for dot prefix, deletion log")

    def test_tmp_extension(self):
        """
        Test for an AIP with filename.tmp files to delete.
        """
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_tmp_copy'), os.path.join(aips_dir, 'aip-id_tmp'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_tmp', 'title', 1, True)
        delete_temp(aip)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%#m-%#d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = aip_directory_print(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    deletion_log,
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with test for .tmp extension, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log['Deletions']
        expected_aip_log = 'File(s) deleted'
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for .tmp extension, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                            [os.path.join(aip_path, 'Text.tmp'), 'Text.tmp', 9, today],
                            [os.path.join(aip_path, 'Test Dir', 'Test Dir Text.tmp'),
                             'Test Dir Text.tmp', 1615, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for .tmp extension, deletion log")


if __name__ == "__main__":
    unittest.main()
