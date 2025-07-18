"""Testing for the function delete_temp, which takes an AIP class instance as input,
deletes temporary files based on the file names, and logs what was deleted, if anything.

There are two separate unit tests for each type of temporary file,
one that tests the file is deleted and the AIP log is updated correctly and
one that tests that the files deleted log is made correctly."""

import datetime
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
    df["Date Last Modified"] = df["Date Last Modified"].str.split(" ").str[0]
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
        # Makes the input needed for the function (AIP class instance and AIP folder with test files)
        # and runs the function being tested.
        aip = AIP(os.getcwd(), "test", None, "coll-1", "no-temp", "general", "aip-id", "title", 1, True)
        delete_temp(aip)

        # Test for the AIP folder.
        result = aip_directory_print(aip.id)
        expected = [os.path.join(aip.id, "Test Dir"),
                    os.path.join(aip.id, "Text.txt"),
                    os.path.join(aip.id, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with test for no temporary files, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log["Deletions"]
        expected_aip_log = "No files deleted"
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for no temporary files, AIP log")

    def test_ds_store(self):
        """
        Test for an AIP with .DS_Store files to delete.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files)
        # and runs the function being tested.
        aip = AIP(os.getcwd(), "test", None, "coll-1", "ds-store", "general", "aip-id_ds-store", "title", 1, True)
        delete_temp(aip)

        # Variables used throughout the test: the path to the deletion log and today"s date formatted YYYY-M-D.
        deletion_log = os.path.join(aip.id, f"{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv")
        today = datetime.datetime.today().strftime("%Y-%#m-%#d")

        # Test for the AIP folder.
        result = aip_directory_print(aip.id)
        expected = [os.path.join(aip.id, "Test Dir"),
                    deletion_log,
                    os.path.join(aip.id, "Text.txt"),
                    os.path.join(aip.id, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with test for .DS_Store, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log["Deletions"]
        expected_aip_log = "File(s) deleted"
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for .DS_Store, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [["Path", "File Name", "Size (Bytes)", "Date Last Modified"],
                            [os.path.join("ds-store-id", ".DS_Store"), ".DS_Store", 4, today],
                            [os.path.join("ds-store-id", "Test Dir", ".DS_Store"), ".DS_Store", 4, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for .DS_Store, deletion log")

    def test_ds_store_2(self):
        """
        Test for an AIP with ._.DS_Store files to delete.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files)
        # and runs the function being tested.
        aip = AIP(os.getcwd(), "test", None, "coll-1", "ds-store-2", "general", "aip-id_ds-store-2", "title", 1, True)
        delete_temp(aip)

        # Variables used throughout the test: the path to the deletion log and today"s date formatted YYYY-M-D.
        deletion_log = os.path.join(aip.id, f"{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv")
        today = datetime.datetime.today().strftime("%Y-%#m-%#d")

        # Test for the AIP folder.
        result = aip_directory_print(aip.id)
        expected = [os.path.join(aip.id, "Test Dir"),
                    deletion_log,
                    os.path.join(aip.id, "Text.txt"),
                    os.path.join(aip.id, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with test for ._.DS_Store, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log["Deletions"]
        expected_aip_log = "File(s) deleted"
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for ._.DS_Store, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [["Path", "File Name", "Size (Bytes)", "Date Last Modified"],
                            [os.path.join("ds-store-2-id", "._.DS_Store"), "._.DS_Store", 4, today],
                            [os.path.join("ds-store-2-id", "Test Dir", "._.DS_Store"), "._.DS_Store", 4, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for .DS_Store, deletion log")

    def test_thumbs_db(self):
        """
        Test for an AIP with Thumbs.db files to delete.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files)
        # and runs the function being tested.
        aip = AIP(os.getcwd(), "test", None, "coll-1", "thumbs-db", "general", "aip-id_thumbs", "title", 1, True)
        delete_temp(aip)

        # Variables used throughout the test: the path to the deletion log and today"s date formatted YYYY-M-D.
        deletion_log = os.path.join(aip.id, f"{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv")
        today = datetime.datetime.today().strftime("%Y-%#m-%#d")

        # Test for the AIP folder.
        result = aip_directory_print(aip.id)
        expected = [os.path.join(aip.id, "Test Dir"),
                    os.path.join(aip.id, "Text.txt"),
                    deletion_log,
                    os.path.join(aip.id, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with test for Thumbs.db, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log["Deletions"]
        expected_aip_log = "File(s) deleted"
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for Thumbs.db, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [["Path", "File Name", "Size (Bytes)", "Date Last Modified"],
                            [os.path.join("thumbs-id", "Thumbs.db"), "Thumbs.db", 4, today],
                            [os.path.join("thumbs-id", "Test Dir", "Thumbs.db"), "Thumbs.db", 4, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for Thumbs.db, deletion log")

    def test_dot_prefix(self):
        """
        Test for an AIP with .filename files to delete.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files)
        # and runs the function being tested.
        aip = AIP(os.getcwd(), "test", None, "coll-1", "dot-filename", "general", "aip-id_dot", "title", 1, True)
        delete_temp(aip)

        # Variables used throughout the test: the path to the deletion log and today"s date formatted YYYY-M-D.
        deletion_log = os.path.join(aip.id, f"{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv")
        today = datetime.datetime.today().strftime("%Y-%#m-%#d")

        # Test for the AIP folder.
        result = aip_directory_print(aip.id)
        expected = [os.path.join(aip.id, "Test Dir"),
                    deletion_log,
                    os.path.join(aip.id, "Text.txt"),
                    os.path.join(aip.id, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with test for dot prefix, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log["Deletions"]
        expected_aip_log = "File(s) deleted"
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for dot prefix, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [["Path", "File Name", "Size (Bytes)", "Date Last Modified"],
                            [os.path.join("dot-id", ".temporary.txt"), ".temporary.txt", 4, today],
                            [os.path.join("dot-id", "Test Dir", ".temporary.txt"), ".temporary.txt", 4, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for dot prefix, deletion log")

    def test_tmp_extension(self):
        """
        Test for an AIP with filename.tmp files to delete.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files)
        # and runs the function being tested.
        aip = AIP(os.getcwd(), "test", None, "coll-1", "filename-tmp", "general", "aip-id_tmp", "title", 1, True)
        delete_temp(aip)

        # Variables used throughout the test: the path to the deletion log and today"s date formatted YYYY-M-D.
        deletion_log = os.path.join(aip.id, f"{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv")
        today = datetime.datetime.today().strftime("%Y-%#m-%#d")

        # Test for the AIP folder.
        result = aip_directory_print(aip.id)
        expected = [os.path.join(aip.id, "Test Dir"),
                    os.path.join(aip.id, "Text.txt"),
                    deletion_log,
                    os.path.join(aip.id, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with test for .tmp extension, AIP folder")

        # Test for the AIP log.
        result_aip_log = aip.log["Deletions"]
        expected_aip_log = "File(s) deleted"
        self.assertEqual(result_aip_log, expected_aip_log, "Problem with test for .tmp extension, AIP log")

        # Test for the deletion log.
        result_del_log = deletion_log_rows(deletion_log)
        expected_del_log = [["Path", "File Name", "Size (Bytes)", "Date Last Modified"],
                            [os.path.join("tmp-id", "temporary.tmp"), "temporary.tmp", 4, today],
                            [os.path.join("tmp-id", "Test Dir", "temporary.tmp"), "temporary.tmp", 4, today]]
        self.assertEqual(result_del_log, expected_del_log, "Problem with test for .tmp extension, deletion log")


if __name__ == "__main__":
    unittest.main()
