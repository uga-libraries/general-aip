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
    elif aip_id == 'sort-coll':
        with open(os.path.join(aip_id, 'sort-coll_coll.csv'), 'w') as file:
            file.write('Collection Test File')
    elif aip_id == 'sort-collscope':
        with open(os.path.join(aip_id, 'sort-collscope_collscope.csv'), 'w') as file:
            file.write('Collection Scope Test File')
    elif aip_id == 'sort-crawldef':
        with open(os.path.join(aip_id, 'sort-crawldef_crawldef.csv'), 'w') as file:
            file.write('Crawl Definition Test File')
    elif aip_id == 'sort-crawljob':
        with open(os.path.join(aip_id, 'sort-crawljob_crawljob.csv'), 'w') as file:
            file.write('Crawl Job Test File')
    elif aip_id == 'sort-emory':
        with open(os.path.join(aip_id, 'EmoryMD_Test.txt'), 'w') as file:
            file.write('Emory Metadata Test File')
    elif aip_id == 'sort-seed':
        with open(os.path.join(aip_id, 'sort-seed_seed.csv'), 'w') as file:
            file.write('Seed Test File')
    elif aip_id == 'sort-seedscope':
        with open(os.path.join(aip_id, 'sort-seedscope_seedscope.csv'), 'w') as file:
            file.write('Seed Scope Test File')
    elif aip_id == 'sort-log':
        with open(os.path.join(aip_id, 'sort-log_files-deleted_2022-10-31_del.csv'), 'w') as file:
            file.write('Deletion Log Test File')


def aip_directory_print(folder):
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

    def tearDown(self):
        """
        Deletes the aip log, errors folder, and test AIPs folders, if present.
        """
        if os.path.exists(os.path.join('..', 'aip_log.csv')):
            os.remove(os.path.join('..', 'aip_log.csv'))

        paths = (os.path.join('..', 'errors'), 'sort-coll', 'sort-collscope', 'sort-crawldef', 'sort-crawljob',
                 'sort-emory', 'sort-log', 'sort-none', 'sort-seed', 'sort-seedscope')
        for path in paths:
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_error_objects_exists(self):
        """
        Test for error handling when there is already an objects subfolder and no metadata subfolder.
        Result for testing is the files and folders within the AIPs folder plus the AIP log.
        """
        objects_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-objects', 'err-objects', 'title', 1, True)
        make_aip_directory('err-objects')
        structure_directory(objects_aip)

        aip_path = os.path.join('..', 'errors', 'objects_folder_exists', 'err-objects')
        result = (aip_directory_print(aip_path),
                  objects_aip.log['ObjectsError'],
                  objects_aip.log['MetadataError'])

        expected = ([os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')],
                    'Objects folder already exists in original files',
                    'n/a')

        self.assertEqual(result, expected, 'Problem with error - objects exists')

    def test_error_both_exist(self):
        """
        Test for structuring an AIP when there are already objects and metadata subfolders.
        Result for testing is the files and folders within the AIPs folder plus the AIP log.
        """
        both_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-both', 'err-both', 'title', 1, True)
        make_aip_directory('err-both')
        structure_directory(both_aip)

        aip_path = os.path.join('..', 'errors', 'objects_folder_exists', 'err-both')
        result = (aip_directory_print(aip_path),
                  both_aip.log['ObjectsError'],
                  both_aip.log['MetadataError'])

        expected = ([os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')],
                    'Objects folder already exists in original files',
                    'n/a')

        self.assertEqual(result, expected, 'Problem with error - metadata and objects exists')

    def test_error_metadata_exists(self):
        """
        Test for structuring an AIP when there is already a metadata subfolder and no objects subfolder.
        Result for testing is the files and folders within the AIPs folder plus the AIP log.
        """
        metadata_aip = AIP(os.getcwd(), 'test', 'coll-1', 'err-metadata', 'err-metadata', 'title', 1, True)
        make_aip_directory('err-metadata')
        structure_directory(metadata_aip)

        aip_path = os.path.join('..', 'errors', 'metadata_folder_exists', 'err-metadata')
        result = (aip_directory_print(aip_path),
                  metadata_aip.log['ObjectsError'],
                  metadata_aip.log['MetadataError'])

        expected = ([os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt')],
                    'n/a',
                    'Metadata folder already exists in original files')

        self.assertEqual(result, expected, 'Problem with error - metadata exists')

    def test_sort_coll(self):
        """
        Test for structuring an AIP which contains an Archive-It collection report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        Result for testing is the files and folders within the AIP folder plus the AIP log.
        """
        aip = AIP(os.getcwd(), 'magil', 'magil-0000', 'sort-coll', 'sort-coll', 'title', 1, True)
        make_aip_directory('sort-coll')
        structure_directory(aip)

        # Test for contents of the AIP folder.
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join('sort-coll', 'metadata'),
                    os.path.join('sort-coll', 'objects'),
                    os.path.join('sort-coll', 'metadata', 'sort-coll_coll.csv'),
                    os.path.join('sort-coll', 'objects', 'Test Dir'),
                    os.path.join('sort-coll', 'objects', 'Text 2.txt'),
                    os.path.join('sort-coll', 'objects', 'Text.txt'),
                    os.path.join('sort-coll', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with sort coll, AIP folder')

        # Test for the AIP log.
        result_log = (aip.log['ObjectsError'], aip.log['MetadataError'])
        expected_log = ('Successfully created objects folder', 'Successfully created metadata folder')
        self.assertEqual(result_log, expected_log, 'Problem with sort coll, log')

    def test_sort_collscope(self):
        """
        Test for structuring an AIP which contains an Archive-It collection scope report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        Result for testing is the files and folders within the AIP folder plus the AIP log.
        """
        aip = AIP(os.getcwd(), 'magil', 'magil-0000', 'sort-collscope', 'sort-collscope', 'title', 1, True)
        make_aip_directory('sort-collscope')
        structure_directory(aip)

        # Test for contents of the AIP folder.
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join('sort-collscope', 'metadata'),
                    os.path.join('sort-collscope', 'objects'),
                    os.path.join('sort-collscope', 'metadata', 'sort-collscope_collscope.csv'),
                    os.path.join('sort-collscope', 'objects', 'Test Dir'),
                    os.path.join('sort-collscope', 'objects', 'Text 2.txt'),
                    os.path.join('sort-collscope', 'objects', 'Text.txt'),
                    os.path.join('sort-collscope', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with sort collscope, AIP folder')

        # Test for the AIP log.
        result_log = (aip.log['ObjectsError'], aip.log['MetadataError'])
        expected_log = ('Successfully created objects folder', 'Successfully created metadata folder')
        self.assertEqual(result_log, expected_log, 'Problem with sort collscope, log')

    def test_sort_crawldef(self):
        """
        Test for structuring an AIP which contains an Archive-It crawl definition report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        Result for testing is the files and folders within the AIP folder plus the AIP log.
        """
        aip = AIP(os.getcwd(), 'magil', 'magil-0000', 'sort-crawldef', 'sort-crawldef', 'title', 1, True)
        make_aip_directory('sort-crawldef')
        structure_directory(aip)

        # Test for contents of the AIP folder.
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join('sort-crawldef', 'metadata'),
                    os.path.join('sort-crawldef', 'objects'),
                    os.path.join('sort-crawldef', 'metadata', 'sort-crawldef_crawldef.csv'),
                    os.path.join('sort-crawldef', 'objects', 'Test Dir'),
                    os.path.join('sort-crawldef', 'objects', 'Text 2.txt'),
                    os.path.join('sort-crawldef', 'objects', 'Text.txt'),
                    os.path.join('sort-crawldef', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with sort crawl definition, AIP folder')

        # Test for the AIP log.
        result_log = (aip.log['ObjectsError'], aip.log['MetadataError'])
        expected_log = ('Successfully created objects folder', 'Successfully created metadata folder')
        self.assertEqual(result_log, expected_log, 'Problem with sort crawl definition, log')

    def test_sort_crawljob(self):
        """
        Test for structuring an AIP which contains an Archive-It crawl job report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        Result for testing is the files and folders within the AIP folder plus the AIP log.
        """
        aip = AIP(os.getcwd(), 'magil', 'magil-0000', 'sort-crawljob', 'sort-crawljob', 'title', 1, True)
        make_aip_directory('sort-crawljob')
        structure_directory(aip)

        # Test for contents of the AIP folder.
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join('sort-crawljob', 'metadata'),
                    os.path.join('sort-crawljob', 'objects'),
                    os.path.join('sort-crawljob', 'metadata', 'sort-crawljob_crawljob.csv'),
                    os.path.join('sort-crawljob', 'objects', 'Test Dir'),
                    os.path.join('sort-crawljob', 'objects', 'Text 2.txt'),
                    os.path.join('sort-crawljob', 'objects', 'Text.txt'),
                    os.path.join('sort-crawljob', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with sort crawl job, AIP folder')

        # Test for the AIP log.
        result_log = (aip.log['ObjectsError'], aip.log['MetadataError'])
        expected_log = ('Successfully created objects folder', 'Successfully created metadata folder')
        self.assertEqual(result_log, expected_log, 'Problem with sort crawl job, log')

    def test_sort_emory(self):
        """
        Test for structuring an AIP which contains an Emory metadata file, which goes in the metadata subfolder.
        All other files will go in the objects subfolder.
        Result for testing is the files and folders within the AIPs folder plus the AIP log.
        """
        emory_aip = AIP(os.getcwd(), 'emory', 'coll-1', 'sort-emory', 'sort-emory', 'title', 1, True)
        make_aip_directory('sort-emory')
        structure_directory(emory_aip)

        result = (aip_directory_print(emory_aip.folder_name),
                  emory_aip.log['ObjectsError'],
                  emory_aip.log['MetadataError'])

        expected = ([os.path.join('sort-emory', 'metadata'),
                    os.path.join('sort-emory', 'objects'),
                    os.path.join('sort-emory', 'metadata', 'EmoryMD_Test.txt'),
                    os.path.join('sort-emory', 'objects', 'Test Dir'),
                    os.path.join('sort-emory', 'objects', 'Text 2.txt'),
                    os.path.join('sort-emory', 'objects', 'Text.txt'),
                    os.path.join('sort-emory', 'objects', 'Test Dir', 'Test Dir Text.txt')],
                    'Successfully created objects folder',
                    'Successfully created metadata folder')

        self.assertEqual(result, expected, 'Problem with sort Emory metadata')

    def test_sort_files_deleted(self):
        """
        Test for structuring an AIP which contains a deletion log, which goes in the metadata subfolder.
        All other files will go to the objects subfolder.
        Result for testing is the files and folders within the AIPs folder plus the AIP log.
        """
        log_aip = AIP(os.getcwd(), 'test', 'coll-1', 'sort-log', 'sort-log', 'title', 1, True)
        make_aip_directory('sort-log')
        structure_directory(log_aip)

        result = (aip_directory_print(log_aip.folder_name),
                  log_aip.log['ObjectsError'],
                  log_aip.log['MetadataError'])

        expected = ([os.path.join('sort-log', 'metadata'),
                    os.path.join('sort-log', 'objects'),
                    os.path.join('sort-log', 'metadata', 'sort-log_files-deleted_2022-10-31_del.csv'),
                    os.path.join('sort-log', 'objects', 'Test Dir'),
                    os.path.join('sort-log', 'objects', 'Text 2.txt'),
                    os.path.join('sort-log', 'objects', 'Text.txt'),
                    os.path.join('sort-log', 'objects', 'Test Dir', 'Test Dir Text.txt')],
                    'Successfully created objects folder',
                    'Successfully created metadata folder')

        self.assertEqual(result, expected, 'Problem with sort deletion log')

    def test_sort_none(self):
        """
        Test for structuring an AIP with no metadata files. All files will go in the objects subfolder.
        Result for testing is the files and folders within the AIPs folder plus the AIP log.
        """
        none_aip = AIP(os.getcwd(), 'test', 'coll-1', 'sort-none', 'sort-none', 'title', 1, True)
        make_aip_directory('sort-none')
        structure_directory(none_aip)

        result = (aip_directory_print(none_aip.folder_name),
                  none_aip.log['ObjectsError'],
                  none_aip.log['MetadataError'])

        expected = ([os.path.join('sort-none', 'metadata'),
                    os.path.join('sort-none', 'objects'),
                    os.path.join('sort-none', 'objects', 'Test Dir'),
                    os.path.join('sort-none', 'objects', 'Text 2.txt'),
                    os.path.join('sort-none', 'objects', 'Text.txt'),
                    os.path.join('sort-none', 'objects', 'Test Dir', 'Test Dir Text.txt')],
                    'Successfully created objects folder',
                    'Successfully created metadata folder')

        self.assertEqual(result, expected, 'Problem with sort no metadata')

    def test_sort_seed(self):
        """
        Test for structuring an AIP which contains an Archive-It seed report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        Result for testing is the files and folders within the AIP folder plus the AIP log.
        """
        aip = AIP(os.getcwd(), 'magil', 'magil-0000', 'sort-seed', 'sort-seed', 'title', 1, True)
        make_aip_directory('sort-seed')
        structure_directory(aip)

        # Test for contents of the AIP folder.
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join('sort-seed', 'metadata'),
                    os.path.join('sort-seed', 'objects'),
                    os.path.join('sort-seed', 'metadata', 'sort-seed_seed.csv'),
                    os.path.join('sort-seed', 'objects', 'Test Dir'),
                    os.path.join('sort-seed', 'objects', 'Text 2.txt'),
                    os.path.join('sort-seed', 'objects', 'Text.txt'),
                    os.path.join('sort-seed', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with sort seed, AIP folder')

        # Test for the AIP log.
        result_log = (aip.log['ObjectsError'], aip.log['MetadataError'])
        expected_log = ('Successfully created objects folder', 'Successfully created metadata folder')
        self.assertEqual(result_log, expected_log, 'Problem with sort seed, log')

    def test_sort_seedscope(self):
        """
        Test for structuring an AIP which contains an Archive-It seed scope report,
        which goes in the metadata subfolder. All other files will go in the objects subfolder.
        Result for testing is the files and folders within the AIP folder plus the AIP log.
        """
        aip = AIP(os.getcwd(), 'magil', 'magil-0000', 'sort-seedscope', 'sort-seedscope', 'title', 1, True)
        make_aip_directory('sort-seedscope')
        structure_directory(aip)

        # Test for contents of the AIP folder.
        result = aip_directory_print(aip.folder_name)
        expected = [os.path.join('sort-seedscope', 'metadata'),
                    os.path.join('sort-seedscope', 'objects'),
                    os.path.join('sort-seedscope', 'metadata', 'sort-seedscope_seedscope.csv'),
                    os.path.join('sort-seedscope', 'objects', 'Test Dir'),
                    os.path.join('sort-seedscope', 'objects', 'Text 2.txt'),
                    os.path.join('sort-seedscope', 'objects', 'Text.txt'),
                    os.path.join('sort-seedscope', 'objects', 'Test Dir', 'Test Dir Text.txt')]
        self.assertEqual(result, expected, 'Problem with sort seed scope, AIP folder')

        # Test for the AIP log.
        result_log = (aip.log['ObjectsError'], aip.log['MetadataError'])
        expected_log = ('Successfully created objects folder', 'Successfully created metadata folder')
        self.assertEqual(result_log, expected_log, 'Problem with sort seed scope, metadata')


if __name__ == '__main__':
    unittest.main()
