"""Testing for the function structure_directory, which takes an AIP class instance as input and
organizes the contents of the AIP folder into metadata and objects subfolders.
There is error handling for if a folder named objects or metadata already exists in the AIP folder.
There are a few files that are sorted into metadata and everything else goes into objects.

KNOWN ISSUE: permissions error for copying web, so that test isn't working.
"""

import os
import shutil
import unittest
from aip_functions import AIP, structure_directory


def aips_directory_list(folder):
    """
    Makes and returns a list with the filepath for every folder and file in an AIP folder.
    The list is sorted because the list can be in a different order depending on the operating system.
    This is used to compare the structure_directory function's actual results to the expected results.
    """
    directory_list = []
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            directory_list.append(os.path.join(root, directory))
        for file in files:
            directory_list.append(os.path.join(root, file))
    directory_list.sort(key=str.lower)
    return directory_list


class TestStructureDirectory(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the aip log, errors folder, and test AIPs folders, if present.
        """
        # Deletes error folder from staging.
        error_folder = os.path.join(os.getcwd(), 'staging', 'aips-with-errors')
        if os.path.exists(error_folder):
            shutil.rmtree(error_folder)

        # Deletes log from aips_directory
        log_path = os.path.join(os.getcwd(), 'structure_directory', 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        # Deletes AIP folders from aips_directory.
        aip_folders = ('deletion-aip-1', 'emory-aip-1', 'error-aip-1', 'error-aip-2',
                       'error-aip-3', 'objects-aip-1', 'web-aip-1')
        for aip_folder in aip_folders:
            aip_folder_path = os.path.join(os.getcwd(), 'structure_directory', aip_folder)
            if os.path.exists(aip_folder_path):
                shutil.rmtree(aip_folder_path)

    def test_error_objects_exists(self):
        """
        Test for error handling when the AIP folder already contains a folder named objects.
        """
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-1', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'error-aip-1_copy'), os.path.join(aips_dir, 'error-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, 'aips-with-errors', 'objects_folder_exists', 'error-aip-1')
        result = aips_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt')]
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
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-2', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'error-aip-2_copy'), os.path.join(aips_dir, 'error-aip-2'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, 'aips-with-errors', 'objects_folder_exists', 'error-aip-2')
        result = aips_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt')]
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
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-3', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'error-aip-3_copy'), os.path.join(aips_dir, 'error-aip-3'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        # It contains the objects folder because the script made it before finding the metadata folder exists error.
        aip_path = os.path.join(staging_dir, 'aips-with-errors', 'metadata_folder_exists', 'error-aip-3')
        result = aips_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt')]
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
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'emory', None, 'coll-emory', 'folder', 'general', 'emory-aip-1', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'emory-aip-1_copy'), os.path.join(aips_dir, 'emory-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = aips_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'EmoryMD_Text.txt'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Test Dir'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'objects', 'Text 2.txt'),
                    os.path.join(aip_path, 'objects', 'Text.txt')]
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
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-delete', 'folder', 'general', 'deletion-aip-1', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'deletion-aip-1_copy'), os.path.join(aips_dir, 'deletion-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = aips_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'deletion-aip-1_files-deleted_2022-10-31_del.csv'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Test Dir'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'objects', 'Text 2.txt'),
                    os.path.join(aip_path, 'objects', 'Text.txt')]
        self.assertEqual(result, expected, "Problem with sort files deleted log, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Successfully created objects folder'
        self.assertEqual(result_log, expected_log, "Problem with sort files deleted log, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'Successfully created metadata folder'
        self.assertEqual(result_log2, expected_log2, "Problem with sort files deleted log, log: MetadataError")

    def test_sort_none(self):
        """
        Test for structuring an AIP with no metadata files. All files will go in the objects subfolder.
        Includes files that would be sorted to metadata if the department or AIP ID was different.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll', 'folder', 'genera', 'objects-aip-1', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'objects-aip-1_copy'), os.path.join(aips_dir, 'objects-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = aips_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Test Dir'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'objects', 'Text 2.txt'),
                    os.path.join(aip_path, 'objects', 'Text.txt')]
        self.assertEqual(result, expected, "Problem with sort none (no metadata), AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log['ObjectsError']
        expected_log = 'Successfully created objects folder'
        self.assertEqual(result_log, expected_log, "Problem with sort none (no metadata), log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log['MetadataError']
        expected_log2 = 'Successfully created metadata folder'
        self.assertEqual(result_log2, expected_log2, "Problem with sort none (no metadata), log: MetadataError")

    def test_sort_web(self):
        """
        Test for structuring an AIP which contains the six Archive-It reports,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'magil', None, 'coll-web', 'folder', 'web', 'web-aip-1', 'title', 1, True)
        shutil.copytree(os.path.join(aips_dir, 'web-aip-1_copy'), os.path.join(aips_dir, 'web-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = aips_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_coll.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_collscope.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_crawldef.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_crawljob.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_seed.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_seedscope.csv'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Test Dir'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'objects', 'Text 2.txt'),
                    os.path.join(aip_path, 'objects', 'Text.txt')]
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
