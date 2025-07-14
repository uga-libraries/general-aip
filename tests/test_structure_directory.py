"""Testing for the function structure_directory, which takes an AIP class instance as input and
organizes the contents of the AIP folder into metadata and objects subfolders.
There is error handling for if a folder named objects or metadata already exists in the AIP folder.
There are a few files that are sorted into metadata and everything else goes into objects.

KNOWN ISSUE: these tests must be run one at a time, due to how setting the current directory to aips_directory is done.
We will be removing reliance on current working directory soon, which will resolve this issue.
"""

import os
import shutil
import unittest
from aip_functions import AIP, log, structure_directory


# def make_aip_directory(aip_id):
#     """
#     Makes a folder for an AIP with test files in the current working directory.
#     All have at least three text files and one folder.
#     Some have additional files and folders needed for their test.
#     """
#     # Folders and files used in every test.
#     os.mkdir(aip_id)
#     os.mkdir(os.path.join(aip_id, "Test Dir"))
#     with open(os.path.join(aip_id, "Text.txt"), "w") as test_file:
#         test_file.write("Test File")
#     with open(os.path.join(aip_id, "Text 2.txt"), "w") as test_file:
#         test_file.write("Test File 2")
#     with open(os.path.join(aip_id, "Test Dir", "Test Dir Text.txt"), "w") as test_file:
#         test_file.write("Test File 3")
#
#     # Folders and files used for a specific test.
#     if aip_id == "err-objects":
#         os.mkdir(os.path.join(aip_id, "objects"))
#         with open(os.path.join(aip_id, "objects", "Objects Text.txt"), "w") as test_file:
#             test_file.write("Test File Objects")
#     elif aip_id == "err-both":
#         os.mkdir(os.path.join(aip_id, "objects"))
#         with open(os.path.join(aip_id, "objects", "Objects Text.txt"), "w") as test_file:
#             test_file.write("Test File Objects")
#         os.mkdir(os.path.join(aip_id, "metadata"))
#         with open(os.path.join(aip_id, "metadata", "Metadata Text.txt"), "w") as test_file:
#             test_file.write("Test File Metadata")
#     elif aip_id == "err-metadata":
#         os.mkdir(os.path.join(aip_id, "metadata"))
#         with open(os.path.join(aip_id, "metadata", "Metadata Text.txt"), "w") as test_file:
#             test_file.write("Test File Metadata")
#     elif aip_id == "sort-coll":
#         with open(os.path.join(aip_id, "sort-coll_coll.csv"), "w") as test_file:
#             test_file.write("Collection Test File")
#     elif aip_id == "sort-collscope":
#         with open(os.path.join(aip_id, "sort-collscope_collscope.csv"), "w") as test_file:
#             test_file.write("Collection Scope Test File")
#     elif aip_id == "sort-crawldef":
#         with open(os.path.join(aip_id, "sort-crawldef_crawldef.csv"), "w") as test_file:
#             test_file.write("Crawl Definition Test File")
#     elif aip_id == "sort-crawljob":
#         with open(os.path.join(aip_id, "sort-crawljob_crawljob.csv"), "w") as test_file:
#             test_file.write("Crawl Job Test File")
#     elif aip_id == "sort-emory":
#         with open(os.path.join(aip_id, "EmoryMD_Test.txt"), "w") as test_file:
#             test_file.write("Emory Metadata Test File")
#     elif aip_id == "sort-none":
#         with open(os.path.join(aip_id, "EmoryMD_Test.txt"), "w") as test_file:
#             test_file.write("Emory Metadata Test File: should not sort")
#         with open(os.path.join(aip_id, "sort-seed_seed.csv"), "w") as test_file:
#             test_file.write("Seed Test File: short not sort")
#     elif aip_id == "sort-seed":
#         with open(os.path.join(aip_id, "sort-seed_seed.csv"), "w") as test_file:
#             test_file.write("Seed Test File")
#     elif aip_id == "sort-seedscope":
#         with open(os.path.join(aip_id, "sort-seedscope_seedscope.csv"), "w") as test_file:
#             test_file.write("Seed Scope Test File")
#     elif aip_id == "sort-log":
#         with open(os.path.join(aip_id, "sort-log_files-deleted_2022-10-31_del.csv"), "w") as test_file:
#             test_file.write("Deletion Log Test File")


def aip_directory_list(folder):
    """
    Makes and returns a list with the filepath for every folder and file in an AIP folder.
    This is used to compare the structure_directory function's actual results to the expected results.
    """
    directory_list = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            directory_list.append(os.path.join(root, directory))
        for file in files:
            directory_list.append(os.path.join(root, file))
    return directory_list


class TestStructureDirectory(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the aip log, errors folder, and test AIPs folders, if present.
        """
        if os.path.exists(os.path.join('..', 'aip_log.csv')):
            os.remove(os.path.join('..', 'aip_log.csv'))

        folders = ('aips-with-errors', 'deletion-aip-1', 'emory-aip-1', 'error-aip-1', 'error-aip-2',
                   'error-aip-3', 'web-aip-1')
        for folder in folders:
            if os.path.exists(folder):
                shutil.rmtree(folder)

    def test_error_objects_exists(self):
        """
        Test for error handling when the AIP folder already contains a folder named objects.
        """
        # Makes test input and runs the function being tested.
        # Current directory needs to be aip_dir until update structure_directory() to use absolute paths.
        aip_dir = os.path.join(os.getcwd(), 'structure_directory')
        os.chdir(aip_dir)
        aip = AIP(aip_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-1', 'title', 1, True)
        shutil.copytree('error-aip-1_copy', 'error-aip-1')
        structure_directory(aip, os.getcwd())

        # Test for the contents of the AIP folder.
        aip_path = os.path.join('aips-with-errors', 'objects_folder_exists', 'error-aip-1')
        result = aip_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with error - objects exists, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Objects folder already exists in original files'
        self.assertEqual(result_log, expected_log, 'Problem with error - objects exists, log: ObjectsError')

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'n/a'
        self.assertEqual(result_log2, expected_log2, "Problem with error - objects exists, log: MetadataError")

        # Test for the AIP log: Complete.
        result_log3 = aip.log['Complete']
        expected_log3 = 'Error during processing'
        self.assertEqual(result_log3, expected_log3, "Problem with error - objects exists, log: Complete")

    def test_error_both_exist(self):
        """
        Test for error handling when the AIP folder already contains folders named metadata and objects.
        """
        # Makes test input and runs the function being tested.
        # Current directory needs to be aip_dir until update structure_directory() to use absolute paths.
        aip_dir = os.path.join(os.getcwd(), 'structure_directory')
        os.chdir(aip_dir)
        aip = AIP(aip_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-2', 'title', 1, True)
        shutil.copytree('error-aip-2_copy', 'error-aip-2')
        structure_directory(aip, os.getcwd())

        # Test for the contents of the AIP folder.
        aip_path = os.path.join('aips-with-errors', 'objects_folder_exists', 'error-aip-2')
        result = aip_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with error - both exist, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Objects folder already exists in original files'
        self.assertEqual(result_log, expected_log, "Problem with error - both exist, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'n/a'
        self.assertEqual(result_log2, expected_log2, "Problem with error - both exist, log: MetadataError")

        # Test for the AIP log: Complete.
        result_log3 = aip.log['Complete']
        expected_log3 = 'Error during processing'
        self.assertEqual(result_log3, expected_log3, "Problem with error - both exist, log: Complete")

    def test_error_metadata_exists(self):
        """
        Test for error handling when the AIP folder already contains a folder named metadata.
        """
        # Makes test input and runs the function being tested.
        # Current directory needs to be aip_dir until update structure_directory() to use absolute paths.
        aip_dir = os.path.join(os.getcwd(), 'structure_directory')
        os.chdir(aip_dir)
        aip = AIP(aip_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-3', 'title', 1, True)
        shutil.copytree('error-aip-3_copy', 'error-aip-3')
        structure_directory(aip, os.getcwd())

        # Test for the contents of the AIP folder.
        # It contains the objects folder because the script made it before finding the metadata folder exists error.
        aip_path = os.path.join('aips-with-errors', 'metadata_folder_exists', 'error-aip-3')
        result = aip_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with error - metadata exists, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Successfully created objects folder'
        self.assertEqual(result_log, expected_log, "Problem with error - metadata exists, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'Metadata folder already exists in original files'
        self.assertEqual(result_log2, expected_log2, "Problem with error - metadata exists, log: MetadataError")

        # Test for the AIP log: Complete.
        result_log3 = aip.log['Complete']
        expected_log3 = 'Error during processing'
        self.assertEqual(result_log3, expected_log3, "Problem with error - metadata exists, log: Complete")

    def test_sort_emory(self):
        """
        Test for structuring an AIP which contains an Emory metadata file, which goes in the metadata subfolder.
        All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        # Current directory needs to be aip_dir until update structure_directory() to use absolute paths.
        aip_dir = os.path.join(os.getcwd(), 'structure_directory')
        os.chdir(aip_dir)
        aip = AIP(aip_dir, 'emory', None, 'coll-emory', 'folder', 'general', 'emory-aip-1', 'title', 1, True)
        shutil.copytree('emory-aip-1_copy', 'emory-aip-1')
        structure_directory(aip, os.getcwd())

        # Test for the contents of the AIP folder.
        result = aip_directory_list('emory-aip-1')
        expected = [os.path.join('emory-aip-1', 'metadata'),
                    os.path.join('emory-aip-1', 'objects'),
                    os.path.join('emory-aip-1', 'metadata', 'EmoryMD_Text.txt'),
                    os.path.join('emory-aip-1', 'objects', 'Test Dir'),
                    os.path.join('emory-aip-1', 'objects', 'Text 2.txt'),
                    os.path.join('emory-aip-1', 'objects', 'Text.txt'),
                    os.path.join('emory-aip-1', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with sort Emory metadata, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Successfully created objects folder'
        self.assertEqual(result_log, expected_log, "Problem with sort Emory metadata, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'Successfully created metadata folder'
        self.assertEqual(result_log2, expected_log2, "Problem with sort Emory metadata, log: MetadataError")

    def test_sort_files_deleted(self):
        """
        Test for structuring an AIP which contains a deletion log, which goes in the metadata subfolder.
        All other files will go to the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        # Current directory needs to be aip_dir until update structure_directory() to use absolute paths.
        aip_dir = os.path.join(os.getcwd(), 'structure_directory')
        os.chdir(aip_dir)
        aip = AIP(aip_dir, 'dept', None, 'coll-delete', 'folder', 'general', 'deletion-aip-1', 'title', 1, True)
        shutil.copytree('deletion-aip-1_copy', 'deletion-aip-1')
        structure_directory(aip, os.getcwd())

        # Test for the contents of the AIP folder.
        result = aip_directory_list('deletion-aip-1')
        expected = [os.path.join('deletion-aip-1', 'metadata'),
                    os.path.join('deletion-aip-1', 'objects'),
                    os.path.join('deletion-aip-1', 'metadata', 'deletion-aip-1_files-deleted_2022-10-31_del.csv'),
                    os.path.join('deletion-aip-1', 'objects', 'Test Dir'),
                    os.path.join('deletion-aip-1', 'objects', 'Text 2.txt'),
                    os.path.join('deletion-aip-1', 'objects', 'Text.txt'),
                    os.path.join('deletion-aip-1', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with sort files deleted log, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Successfully created objects folder'
        self.assertEqual(result_log, expected_log, "Problem with sort files deleted log, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'Successfully created metadata folder'
        self.assertEqual(result_log2, expected_log2, "Problem with sort files deleted log, log: MetadataError")

    # def test_sort_none(self):
    #     """
    #     Test for structuring an AIP with no metadata files. All files will go in the objects subfolder.
    #     Includes files that would be sorted to metadata if the department or AIP ID was different.
    #     """
    #     # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
    #     # Current directory needs to be aip_dir until update structure_directory() to use absolute paths.
    #     aip_dir = os.path.join(os.getcwd(), "structure_directory")
    #     os.chdir(aip_dir)
    #     aip = AIP(os.getcwd(), "test", "coll-1", "sort-none", "sort-none", "title", 1, True)
    #     make_aip_directory("sort-none")
    #     structure_directory(aip)
    #
    #     # Test for the contents of the AIP folder.
    #     result = aip_directory_list(aip.folder_name)
    #     expected = [os.path.join("sort-none", "metadata"),
    #                 os.path.join("sort-none", "objects"),
    #                 os.path.join("sort-none", "objects", "Test Dir"),
    #                 os.path.join("sort-none", "objects", "EmoryMD_Test.txt"),
    #                 os.path.join("sort-none", "objects", "sort-seed_seed.csv"),
    #                 os.path.join("sort-none", "objects", "Text 2.txt"),
    #                 os.path.join("sort-none", "objects", "Text.txt"),
    #                 os.path.join("sort-none", "objects", "Test Dir", "Test Dir Text.txt")]
    #     self.assertEqual(result, expected, "Problem with sort no metadata, AIP folder")
    #
    #     # Test for the AIP log: ObjectsError.
    #     result_log = aip.log["ObjectsError"]
    #     expected_log = "Successfully created objects folder"
    #     self.assertEqual(result_log, expected_log, "Problem with sort no metadata, log: ObjectsError")
    #
    #     # Test for the AIP log: MetadataError.
    #     result_log2 = aip.log["MetadataError"]
    #     expected_log2 = "Successfully created metadata folder"
    #     self.assertEqual(result_log2, expected_log2, "Problem with sort no metadata, log: MetadataError")
    #
    def test_sort_web(self):
        """
        Test for structuring an AIP which contains the six Archive-It reports,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        # Current directory needs to be aip_dir until update structure_directory() to use absolute paths.
        aip_dir = os.path.join(os.getcwd(), 'structure_directory')
        os.chdir(aip_dir)
        aip = AIP(aip_dir, 'magil', None, 'coll-web', 'folder', 'web', 'web-aip-1', 'title', 1, True)
        shutil.copy('web-aip-1_copy', 'web-aip-1')
        structure_directory(aip, os.getcwd())

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join('web-aip-1', 'metadata'),
                    os.path.join('web-aip-1', 'objects'),
                    os.path.join('web-aip-1', 'metadata', 'web-aip-1_coll.csv'),
                    os.path.join('web-aip-1', 'metadata', 'web-aip-1_collscope.csv'),
                    os.path.join('web-aip-1', 'metadata', 'web-aip-1_crawldef.csv'),
                    os.path.join('web-aip-1', 'metadata', 'web-aip-1_crawljob.csv'),
                    os.path.join('web-aip-1', 'metadata', 'web-aip-1_seed.csv'),
                    os.path.join('web-aip-1', 'metadata', 'web-aip-1_seedscope.csv'),
                    os.path.join('web-aip-1', 'objects', 'Test Dir'),
                    os.path.join('web-aip-1', 'objects', 'Text 2.txt'),
                    os.path.join('web-aip-1', 'objects', 'Text.txt'),
                    os.path.join('web-aip-1', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, "Problem with sort seed, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Successfully created objects folder'
        self.assertEqual(result_log, expected_log, "Problem with sort seed, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'Successfully created metadata folder'
        self.assertEqual(result_log2, expected_log2, "Problem with sort seed, log: MetadataError")


if __name__ == "__main__":
    unittest.main()
