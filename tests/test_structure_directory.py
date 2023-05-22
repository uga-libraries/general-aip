"""Testing for the function structure_directory, which takes an AIP class instance as input and
organizes the contents of the AIP folder into metadata and objects subfolders.
There is error handling for if a folder named objects or metadata already exists in the AIP folder.
There are a few files that are sorted into metadata and everything else goes into objects."""

import os
import shutil
import unittest
from scripts.aip_functions import AIP, log, structure_directory


def make_aip_directory(aip_id):
    """
    Makes a folder for an AIP with test files in the current working directory.
    All have at least three text files and one folder.
    Some have additional files and folders needed for their test.
    """
    # Folders and files used in every test.
    os.mkdir(aip_id)
    os.mkdir(os.path.join(aip_id, "Test Dir"))
    with open(os.path.join(aip_id, "Text.txt"), "w") as test_file:
        test_file.write("Test File")
    with open(os.path.join(aip_id, "Text 2.txt"), "w") as test_file:
        test_file.write("Test File 2")
    with open(os.path.join(aip_id, "Test Dir", "Test Dir Text.txt"), "w") as test_file:
        test_file.write("Test File 3")

    # Folders and files used for a specific test.
    if aip_id == "err-objects":
        os.mkdir(os.path.join(aip_id, "objects"))
        with open(os.path.join(aip_id, "objects", "Objects Text.txt"), "w") as test_file:
            test_file.write("Test File Objects")
    elif aip_id == "err-both":
        os.mkdir(os.path.join(aip_id, "objects"))
        with open(os.path.join(aip_id, "objects", "Objects Text.txt"), "w") as test_file:
            test_file.write("Test File Objects")
        os.mkdir(os.path.join(aip_id, "metadata"))
        with open(os.path.join(aip_id, "metadata", "Metadata Text.txt"), "w") as test_file:
            test_file.write("Test File Metadata")
    elif aip_id == "err-metadata":
        os.mkdir(os.path.join(aip_id, "metadata"))
        with open(os.path.join(aip_id, "metadata", "Metadata Text.txt"), "w") as test_file:
            test_file.write("Test File Metadata")
    elif aip_id == "sort-coll":
        with open(os.path.join(aip_id, "sort-coll_coll.csv"), "w") as test_file:
            test_file.write("Collection Test File")
    elif aip_id == "sort-collscope":
        with open(os.path.join(aip_id, "sort-collscope_collscope.csv"), "w") as test_file:
            test_file.write("Collection Scope Test File")
    elif aip_id == "sort-crawldef":
        with open(os.path.join(aip_id, "sort-crawldef_crawldef.csv"), "w") as test_file:
            test_file.write("Crawl Definition Test File")
    elif aip_id == "sort-crawljob":
        with open(os.path.join(aip_id, "sort-crawljob_crawljob.csv"), "w") as test_file:
            test_file.write("Crawl Job Test File")
    elif aip_id == "sort-emory":
        with open(os.path.join(aip_id, "EmoryMD_Test.txt"), "w") as test_file:
            test_file.write("Emory Metadata Test File")
    elif aip_id == "sort-none":
        with open(os.path.join(aip_id, "EmoryMD_Test.txt"), "w") as test_file:
            test_file.write("Emory Metadata Test File: should not sort")
        with open(os.path.join(aip_id, "sort-seed_seed.csv"), "w") as test_file:
            test_file.write("Seed Test File: short not sort")
    elif aip_id == "sort-seed":
        with open(os.path.join(aip_id, "sort-seed_seed.csv"), "w") as test_file:
            test_file.write("Seed Test File")
    elif aip_id == "sort-seedscope":
        with open(os.path.join(aip_id, "sort-seedscope_seedscope.csv"), "w") as test_file:
            test_file.write("Seed Scope Test File")
    elif aip_id == "sort-log":
        with open(os.path.join(aip_id, "sort-log_files-deleted_2022-10-31_del.csv"), "w") as test_file:
            test_file.write("Deletion Log Test File")


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
        if os.path.exists(os.path.join("..", "aip_log.csv")):
            os.remove(os.path.join("..", "aip_log.csv"))

        paths = (os.path.join("..", "errors"), "sort-coll", "sort-collscope", "sort-crawldef", "sort-crawljob",
                 "sort-emory", "sort-log", "sort-none", "sort-seed", "sort-seedscope")
        for path in paths:
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_error_objects_exists(self):
        """
        Test for error handling when the AIP folder already contains a folder named objects.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "test", "coll-1", "err-objects", "err-objects", "title", 1, True)
        make_aip_directory("err-objects")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join("..", "errors", "objects_folder_exists", "err-objects")
        result = aip_directory_list(aip_path)
        expected = [os.path.join(aip_path, "objects"),
                    os.path.join(aip_path, "Test Dir"),
                    os.path.join(aip_path, "Text 2.txt"),
                    os.path.join(aip_path, "Text.txt"),
                    os.path.join(aip_path, "objects", "Objects Text.txt"),
                    os.path.join(aip_path, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with error - objects exists, AIP folder")

        # Test for the AIP being moved from the AIPs directory.
        # The test for the contents of the AIP folder verifies it is in the error folder.
        result_dir = os.path.exists("err-objects")
        self.assertEqual(result_dir, False, "Problem with error - objects exists, move AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Objects folder already exists in original files"
        self.assertEqual(result_log, expected_log, "Problem with error - objects exists, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "n/a"
        self.assertEqual(result_log2, expected_log2, "Problem with error - objects exists, log: MetadataError")

        # Test for the AIP log: Complete.
        result_log3 = aip.log["Complete"]
        expected_log3 = "Error during processing"
        self.assertEqual(result_log3, expected_log3, "Problem with error - objects exists, log: Complete")

    def test_error_both_exist(self):
        """
        Test for error handling when the AIP folder already contains folders named metadata and objects.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "test", "coll-1", "err-both", "err-both", "title", 1, True)
        make_aip_directory("err-both")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join("..", "errors", "objects_folder_exists", "err-both")
        result = aip_directory_list(aip_path)
        expected = [os.path.join(aip_path, "metadata"),
                    os.path.join(aip_path, "objects"),
                    os.path.join(aip_path, "Test Dir"),
                    os.path.join(aip_path, "Text 2.txt"),
                    os.path.join(aip_path, "Text.txt"),
                    os.path.join(aip_path, "metadata", "Metadata Text.txt"),
                    os.path.join(aip_path, "objects", "Objects Text.txt"),
                    os.path.join(aip_path, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with error - both exist, AIP folder")

        # Test for the AIP being moved from the AIPs directory.
        # The test for the contents of the AIP folder verifies it is in the error folder.
        result_dir = os.path.exists("err-both")
        self.assertEqual(result_dir, False, "Problem with error - both exist, move AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Objects folder already exists in original files"
        self.assertEqual(result_log, expected_log, "Problem with error - both exist, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "n/a"
        self.assertEqual(result_log2, expected_log2, "Problem with error - both exist, log: MetadataError")

        # Test for the AIP log: Complete.
        result_log3 = aip.log["Complete"]
        expected_log3 = "Error during processing"
        self.assertEqual(result_log3, expected_log3, "Problem with error - both exist, log: Complete")

    def test_error_metadata_exists(self):
        """
        Test for error handling when the AIP folder already contains a folder named metadata.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "test", "coll-1", "err-metadata", "err-metadata", "title", 1, True)
        make_aip_directory("err-metadata")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join("..", "errors", "metadata_folder_exists", "err-metadata")
        result = aip_directory_list(aip_path)
        expected = [os.path.join(aip_path, "metadata"),
                    os.path.join(aip_path, "objects"),
                    os.path.join(aip_path, "Test Dir"),
                    os.path.join(aip_path, "Text 2.txt"),
                    os.path.join(aip_path, "Text.txt"),
                    os.path.join(aip_path, "metadata", "Metadata Text.txt"),
                    os.path.join(aip_path, "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with error - metadata exists, AIP folder")

        # Test for the AIP being moved from the AIPs directory.
        # The test for the contents of the AIP folder verifies it is in the error folder.
        result_dir = os.path.exists("err-metadata")
        self.assertEqual(result_dir, False, "Problem with error - metadata exists, move AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with error - metadata exists, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Metadata folder already exists in original files"
        self.assertEqual(result_log2, expected_log2, "Problem with error - metadata exists, log: MetadataError")

        # Test for the AIP log: Complete.
        result_log3 = aip.log["Complete"]
        expected_log3 = "Error during processing"
        self.assertEqual(result_log3, expected_log3, "Problem with error - metadata exists, log: Complete")

    def test_sort_coll(self):
        """
        Test for structuring an AIP which contains an Archive-It collection report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "magil", "magil-0000", "sort-coll", "sort-coll", "title", 1, True)
        make_aip_directory("sort-coll")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-coll", "metadata"),
                    os.path.join("sort-coll", "objects"),
                    os.path.join("sort-coll", "metadata", "sort-coll_coll.csv"),
                    os.path.join("sort-coll", "objects", "Test Dir"),
                    os.path.join("sort-coll", "objects", "Text 2.txt"),
                    os.path.join("sort-coll", "objects", "Text.txt"),
                    os.path.join("sort-coll", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort coll, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort coll, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort coll, log: MetadataError")

    def test_sort_collscope(self):
        """
        Test for structuring an AIP which contains an Archive-It collection scope report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "magil", "magil-0000", "sort-collscope", "sort-collscope", "title", 1, True)
        make_aip_directory("sort-collscope")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-collscope", "metadata"),
                    os.path.join("sort-collscope", "objects"),
                    os.path.join("sort-collscope", "metadata", "sort-collscope_collscope.csv"),
                    os.path.join("sort-collscope", "objects", "Test Dir"),
                    os.path.join("sort-collscope", "objects", "Text 2.txt"),
                    os.path.join("sort-collscope", "objects", "Text.txt"),
                    os.path.join("sort-collscope", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort collscope, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort collscope, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort collscope, log: MetadataError")

    def test_sort_crawldef(self):
        """
        Test for structuring an AIP which contains an Archive-It crawl definition report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "magil", "magil-0000", "sort-crawldef", "sort-crawldef", "title", 1, True)
        make_aip_directory("sort-crawldef")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-crawldef", "metadata"),
                    os.path.join("sort-crawldef", "objects"),
                    os.path.join("sort-crawldef", "metadata", "sort-crawldef_crawldef.csv"),
                    os.path.join("sort-crawldef", "objects", "Test Dir"),
                    os.path.join("sort-crawldef", "objects", "Text 2.txt"),
                    os.path.join("sort-crawldef", "objects", "Text.txt"),
                    os.path.join("sort-crawldef", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort crawl definition, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort crawl definition, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort crawl definition, log: MetadataError")

    def test_sort_crawljob(self):
        """
        Test for structuring an AIP which contains an Archive-It crawl job report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "magil", "magil-0000", "sort-crawljob", "sort-crawljob", "title", 1, True)
        make_aip_directory("sort-crawljob")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-crawljob", "metadata"),
                    os.path.join("sort-crawljob", "objects"),
                    os.path.join("sort-crawljob", "metadata", "sort-crawljob_crawljob.csv"),
                    os.path.join("sort-crawljob", "objects", "Test Dir"),
                    os.path.join("sort-crawljob", "objects", "Text 2.txt"),
                    os.path.join("sort-crawljob", "objects", "Text.txt"),
                    os.path.join("sort-crawljob", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort crawl job, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort crawl job, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort crawl job, log: MetadataError")

    def test_sort_emory(self):
        """
        Test for structuring an AIP which contains an Emory metadata file, which goes in the metadata subfolder.
        All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "emory", "coll-1", "sort-emory", "sort-emory", "title", 1, True)
        make_aip_directory("sort-emory")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-emory", "metadata"),
                    os.path.join("sort-emory", "objects"),
                    os.path.join("sort-emory", "metadata", "EmoryMD_Test.txt"),
                    os.path.join("sort-emory", "objects", "Test Dir"),
                    os.path.join("sort-emory", "objects", "Text 2.txt"),
                    os.path.join("sort-emory", "objects", "Text.txt"),
                    os.path.join("sort-emory", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort Emory metadata, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort Emory metadata, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort Emory metadata, log: MetadataError")

    def test_sort_files_deleted(self):
        """
        Test for structuring an AIP which contains a deletion log, which goes in the metadata subfolder.
        All other files will go to the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "test", "coll-1", "sort-log", "sort-log", "title", 1, True)
        make_aip_directory("sort-log")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-log", "metadata"),
                    os.path.join("sort-log", "objects"),
                    os.path.join("sort-log", "metadata", "sort-log_files-deleted_2022-10-31_del.csv"),
                    os.path.join("sort-log", "objects", "Test Dir"),
                    os.path.join("sort-log", "objects", "Text 2.txt"),
                    os.path.join("sort-log", "objects", "Text.txt"),
                    os.path.join("sort-log", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort files deleted log, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort files deleted log, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort files deleted log, log: MetadataError")

    def test_sort_none(self):
        """
        Test for structuring an AIP with no metadata files. All files will go in the objects subfolder.
        Includes files that would be sorted to metadata if the department or AIP ID was different.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "test", "coll-1", "sort-none", "sort-none", "title", 1, True)
        make_aip_directory("sort-none")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-none", "metadata"),
                    os.path.join("sort-none", "objects"),
                    os.path.join("sort-none", "objects", "Test Dir"),
                    os.path.join("sort-none", "objects", "EmoryMD_Test.txt"),
                    os.path.join("sort-none", "objects", "sort-seed_seed.csv"),
                    os.path.join("sort-none", "objects", "Text 2.txt"),
                    os.path.join("sort-none", "objects", "Text.txt"),
                    os.path.join("sort-none", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort no metadata, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort no metadata, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort no metadata, log: MetadataError")

    def test_sort_seed(self):
        """
        Test for structuring an AIP which contains an Archive-It seed report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "magil", "magil-0000", "sort-seed", "sort-seed", "title", 1, True)
        make_aip_directory("sort-seed")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-seed", "metadata"),
                    os.path.join("sort-seed", "objects"),
                    os.path.join("sort-seed", "metadata", "sort-seed_seed.csv"),
                    os.path.join("sort-seed", "objects", "Test Dir"),
                    os.path.join("sort-seed", "objects", "Text 2.txt"),
                    os.path.join("sort-seed", "objects", "Text.txt"),
                    os.path.join("sort-seed", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort seed, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort seed, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort seed, log: MetadataError")

    def test_sort_seedscope(self):
        """
        Test for structuring an AIP which contains an Archive-It seed scope report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        """
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aip = AIP(os.getcwd(), "magil", "magil-0000", "sort-seedscope", "sort-seedscope", "title", 1, True)
        make_aip_directory("sort-seedscope")
        structure_directory(aip)

        # Test for the contents of the AIP folder.
        result = aip_directory_list(aip.folder_name)
        expected = [os.path.join("sort-seedscope", "metadata"),
                    os.path.join("sort-seedscope", "objects"),
                    os.path.join("sort-seedscope", "metadata", "sort-seedscope_seedscope.csv"),
                    os.path.join("sort-seedscope", "objects", "Test Dir"),
                    os.path.join("sort-seedscope", "objects", "Text 2.txt"),
                    os.path.join("sort-seedscope", "objects", "Text.txt"),
                    os.path.join("sort-seedscope", "objects", "Test Dir", "Test Dir Text.txt")]
        self.assertEqual(result, expected, "Problem with sort seed scope, AIP folder")

        # Test for the AIP log: ObjectsError.
        result_log = aip.log["ObjectsError"]
        expected_log = "Successfully created objects folder"
        self.assertEqual(result_log, expected_log, "Problem with sort seed scope, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result_log2 = aip.log["MetadataError"]
        expected_log2 = "Successfully created metadata folder"
        self.assertEqual(result_log2, expected_log2, "Problem with sort seed scope, log: MetadataError")


if __name__ == "__main__":
    unittest.main()
