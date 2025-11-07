"""Testing for the function delete_temp, which takes an AIP class instance as input,
deletes temporary files based on the file names, and logs what was deleted, if anything.

There are two separate unit tests for each type of temporary file,
one that tests the file is deleted and the AIP log is updated correctly and
one that tests that the files deleted log is made correctly."""

from datetime import date
import os
import shutil
import unittest
from aip_functions import AIP, delete_temp
from test_script import make_deletion_log_list, make_directory_list


class TestDeleteTemp(unittest.TestCase):

    def setUp(self):
        """Date this repo was first cloned to local machine, which is the date info in the deletion log.
        This does need to be reset after syncing with GitHub."""
        self.modified = '2025-11-7'

    def tearDown(self):
        """Deletes the AIP folders created by each test"""
        variations = ['dot', 'ds-store', 'ds-store-2', 'no-log', 'tmp', 'thumbs']
        for variation in variations:
            aip_path = os.path.join(os.getcwd(), 'delete_temp', f'aip-id_{variation}')
            if os.path.exists(aip_path):
                shutil.rmtree(aip_path)

    def test_no_log(self):
        """Test for an AIP with temporary files to delete but deletion should not be logged"""
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_no-log_copy'), os.path.join(aips_dir, 'aip-id_no-log'))
        aip = AIP(aips_dir, 'dept', 'None', 'coll-1', 'folder', 'general', 'aip-id_no-log', 'title', 1, True)
        aip.log['Deletions'] = 'Deletions note (for testing)'
        delete_temp(aip, os.path.join(aips_dir, aip.id), logging=False)

        # Variables used throughout the test: the path to the deletion log and today's date formatted YYYY-MM-DD.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%m-%d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = make_directory_list(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with test for no log, AIP folder")

        # Test for the AIP log.
        result = aip.log['Deletions']
        expected = 'Deletions note (for testing)'
        self.assertEqual(expected, result, "Problem with test for no log, AIP log")

        # Test the deletion log was not made.
        result = os.path.exists(os.path.join(aip_path, deletion_log))
        self.assertEqual(False, result, "Problem with test for no log, deletion log")

    def test_no_temp(self):
        """Test for an AIP with no temporary files to delete"""
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id', 'title', 1, True)
        delete_temp(aip, os.path.join(aips_dir, aip.id), logging=True)

        # Test for the AIP folder.
        aip_path = os.path.join(aips_dir, aip.id)
        result = make_directory_list(os.path.join(aip_path))
        expected = [os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with test for no temporary files, AIP folder")

        # Test for the AIP log.
        result = aip.log['Deletions']
        expected = 'No files deleted'
        self.assertEqual(expected, result, "Problem with test for no temporary files, AIP log")

        # Test the deletion log was not made, since no files were deleted.
        today = date.today().strftime('%Y-%#m-%#d')
        result = os.path.exists(os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv'))
        self.assertEqual(False, result, "Problem with test for no temporary files, deletion log")

    def test_ds_store(self):
        """Test for an AIP with .DS_Store files to delete"""
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_ds-store_copy'), os.path.join(aips_dir, 'aip-id_ds-store'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_ds-store', 'title', 1, True)
        delete_temp(aip, os.path.join(aips_dir, aip.id), logging=True)

        # Variables used throughout the test: the path to the deletion log and today's date formatted YYYY-MM-DD.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%m-%d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = make_directory_list(os.path.join(aip_path))
        expected = [deletion_log,
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with test for .DS_Store, AIP folder")

        # Test for the AIP log.
        result = aip.log['Deletions']
        expected = 'File(s) deleted (see log)'
        self.assertEqual(expected, result, "Problem with test for .DS_Store, AIP log")

        # Test for the deletion log.
        result = make_deletion_log_list(deletion_log)
        expected = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                    [os.path.join(aips_dir, 'aip-id_ds-store', '.DS_Store'), '.DS_Store', 0, self.modified],
                    [os.path.join(aips_dir, 'aip-id_ds-store', 'Test Dir', '.DS_Store'), '.DS_Store', 0, self.modified]]
        self.assertEqual(expected, result, "Problem with test for .DS_Store, deletion log")

    def test_ds_store_2(self):
        """Test for an AIP with ._.DS_Store files to delete"""
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_ds-store-2_copy'), os.path.join(aips_dir, 'aip-id_ds-store-2'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_ds-store-2', 'title', 1, True)
        delete_temp(aip, os.path.join(aips_dir, aip.id), logging=True)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%m-%d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = make_directory_list(os.path.join(aip_path))
        expected = [deletion_log,
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with test for ._.DS_Store, AIP folder")

        # Test for the AIP log.
        result = aip.log['Deletions']
        expected = 'File(s) deleted (see log)'
        self.assertEqual(expected, result, "Problem with test for ._.DS_Store, AIP log")

        # Test for the deletion log.
        result = make_deletion_log_list(deletion_log)
        expected = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                    [os.path.join(aips_dir, 'aip-id_ds-store-2', '._.DS_Store'), '._.DS_Store', 0, self.modified],
                    [os.path.join(aips_dir, 'aip-id_ds-store-2', 'Test Dir', '._.DS_Store'), '._.DS_Store', 0,
                     self.modified]]
        self.assertEqual(expected, result, "Problem with test for .DS_Store, deletion log")

    def test_thumbs_db(self):
        """Test for an AIP with Thumbs.db files to delete"""
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_thumbs_copy'), os.path.join(aips_dir, 'aip-id_thumbs'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_thumbs', 'title', 1, True)
        delete_temp(aip, os.path.join(aips_dir, aip.id), logging=True)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%m-%d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = make_directory_list(os.path.join(aip_path))
        expected = [deletion_log,
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with test for Thumbs.db, AIP folder")

        # Test for the AIP log.
        result = aip.log['Deletions']
        expected = 'File(s) deleted (see log)'
        self.assertEqual(expected, result, "Problem with test for Thumbs.db, AIP log")

        # Test for the deletion log.
        # Size is different depending on the OS.
        result = make_deletion_log_list(deletion_log)
        expected = [[['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                     [os.path.join(aips_dir, 'aip-id_thumbs', 'Thumbs.db'), 'Thumbs.db', 25, self.modified],
                     [os.path.join(aips_dir, 'aip-id_thumbs', 'Test Dir', 'Thumbs.db'), 'Thumbs.db', 2590,
                      self.modified]],
                    [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                     [os.path.join(aips_dir, 'aip-id_thumbs', 'Thumbs.db'), 'Thumbs.db', 25, self.modified],
                     [os.path.join(aips_dir, 'aip-id_thumbs', 'Test Dir', 'Thumbs.db'), 'Thumbs.db', 2495,
                      self.modified]]]
        self.assertIn(result, expected, "Problem with test for Thumbs.db, deletion log")

    def test_dot_prefix(self):
        """Test for an AIP with .filename files to delete"""
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_dot_copy'), os.path.join(aips_dir, 'aip-id_dot'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_dot', 'title', 1, True)
        delete_temp(aip, os.path.join(aips_dir, aip.id), logging=True)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%m-%d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = make_directory_list(os.path.join(aip_path))
        expected = [deletion_log,
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with test for dot prefix, AIP folder")

        # Test for the AIP log.
        result = aip.log['Deletions']
        expected = 'File(s) deleted (see log)'
        self.assertEqual(expected, result, "Problem with test for dot prefix, AIP log")

        # Test for the deletion log.
        result = make_deletion_log_list(deletion_log)
        expected = [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                    [os.path.join(aips_dir, 'aip-id_dot', '.temp.txt'), '.temp.txt', 0, self.modified],
                    [os.path.join(aips_dir, 'aip-id_dot', 'Test Dir', '.temp.txt'), '.temp.txt', 0, self.modified]]
        self.assertEqual(expected, result, "Problem with test for dot prefix, deletion log")

    def test_tmp_extension(self):
        """Test for an AIP with filename.tmp files to delete"""
        # Makes the input needed for the function and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'delete_temp')
        shutil.copytree(os.path.join(aips_dir, 'aip-id_tmp_copy'), os.path.join(aips_dir, 'aip-id_tmp'))
        aip = AIP(aips_dir, 'dept', None, 'coll-1', 'folder', 'general', 'aip-id_tmp', 'title', 1, True)
        delete_temp(aip, os.path.join(aips_dir, aip.id), logging=True)

        # Variables used throughout the tests.
        aip_path = os.path.join(aips_dir, aip.id)
        today = date.today().strftime('%Y-%m-%d')
        deletion_log = os.path.join(aip_path, f'{aip.id}_files-deleted_{today}_del.csv')

        # Test for the AIP folder.
        result = make_directory_list(os.path.join(aip_path))
        expected = [deletion_log,
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with test for .tmp extension, AIP folder")

        # Test for the AIP log.
        result = aip.log['Deletions']
        expected = 'File(s) deleted (see log)'
        self.assertEqual(expected, result, "Problem with test for .tmp extension, AIP log")

        # Test for the deletion log.
        # Size is different depending on the OS.
        result = make_deletion_log_list(deletion_log)
        expected = [[['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                     [os.path.join(aip_path, 'Text.tmp'), 'Text.tmp', 9, self.modified],
                     [os.path.join(aip_path, 'Test Dir', 'Test Dir Text.tmp'), 'Test Dir Text.tmp', 1615,
                      self.modified]],
                    [['Path', 'File Name', 'Size (Bytes)', 'Date Last Modified'],
                     [os.path.join(aip_path, 'Text.tmp'), 'Text.tmp', 9, self.modified],
                     [os.path.join(aip_path, 'Test Dir', 'Test Dir Text.tmp'), 'Test Dir Text.tmp', 1583,
                      self.modified]]]
        self.assertIn(result, expected, "Problem with test for .tmp extension, deletion log")


if __name__ == "__main__":
    unittest.main()
