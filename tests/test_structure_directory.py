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
from test_script import make_directory_list


class TestStructureDirectory(unittest.TestCase):

    def tearDown(self):
        """Delete the aip log, errors folder, and test AIPs folders, if present."""
        # Deletes error folder from staging.
        error_folder = os.path.join(os.getcwd(), 'staging', 'aips-with-errors')
        if os.path.exists(error_folder):
            shutil.rmtree(error_folder)

        # Deletes log from aips_directory
        log_path = os.path.join(os.getcwd(), 'structure_directory', 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        # Deletes AIP folders from aips_directory.
        aip_folders = ('av-aip-1', 'av-aip-2', 'av-aip-3', 'av-aip-4', 'deletion-aip-1', 'emory-aip-1',
                       'error-aip-1', 'error-aip-2', 'error-aip-3', 'none-aip-1', 'web-aip-1', 'web-aip-2')
        for aip_folder in aip_folders:
            aip_folder_path = os.path.join(os.getcwd(), 'structure_directory', aip_folder)
            if os.path.exists(aip_folder_path):
                shutil.rmtree(aip_folder_path)

        # Deletes files copied to movs-to-bag:
        mov_folder = os.path.join(os.getcwd(), 'staging', 'movs-to-bag')
        for file in os.listdir(mov_folder):
            if file.endswith('.mov'):
                os.remove(os.path.join(mov_folder, file))

    def test_error_objects_exists(self):
        """Test for error handling when the AIP folder already contains a folder named objects"""
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-1', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'error-aip-1_copy'), os.path.join(aips_dir, 'error-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, 'aips-with-errors', 'objects_folder_exists', 'error-aip-1')
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with error - objects exists, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Objects folder already exists in original files'
        self.assertEqual(expected, result, 'Problem with error - objects exists, log: ObjectsError')

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'n/a'
        self.assertEqual(expected, result, "Problem with error - objects exists, log: MetadataError")

        # Test for the AIP log: Complete.
        result = aip.log['Complete']
        expected = 'Error during processing'
        self.assertEqual(expected, result, "Problem with error - objects exists, log: Complete")

    def test_error_both_exist(self):
        """Test for error handling when the AIP folder already contains folders named metadata and objects"""
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-2', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'error-aip-2_copy'), os.path.join(aips_dir, 'error-aip-2'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, 'aips-with-errors', 'objects_folder_exists', 'error-aip-2')
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Objects Text.txt'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with error - both exist, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Objects folder already exists in original files'
        self.assertEqual(expected, result, "Problem with error - both exist, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'n/a'
        self.assertEqual(expected, result, "Problem with error - both exist, log: MetadataError")

        # Test for the AIP log: Complete.
        result = aip.log['Complete']
        expected = 'Error during processing'
        self.assertEqual(expected, result, "Problem with error - both exist, log: Complete")

    def test_error_metadata_exists(self):
        """Test for error handling when the AIP folder already contains a folder named metadata"""
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-error', 'folder', 'general', 'error-aip-3', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'error-aip-3_copy'), os.path.join(aips_dir, 'error-aip-3'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        # It contains the objects folder because the script made it before finding the metadata folder exists error.
        aip_path = os.path.join(staging_dir, 'aips-with-errors', 'metadata_folder_exists', 'error-aip-3')
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'Metadata Text.txt'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'Test Dir'),
                    os.path.join(aip_path, 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'Text 2.txt'),
                    os.path.join(aip_path, 'Text.txt')]
        self.assertEqual(expected, result, "Problem with error - metadata exists, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with error - metadata exists, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Metadata folder already exists in original files'
        self.assertEqual(expected, result, "Problem with error - metadata exists, log: MetadataError")

        # Test for the AIP log: Complete.
        result = aip.log['Complete']
        expected = 'Error during processing'
        self.assertEqual(expected, result, "Problem with error - metadata exists, log: Complete")

    def test_sort_av(self):
        """Test for an AV AIP with no metadata files"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'bmac', 'wav', 'coll-bmac', 'folder', 'av', 'av-aip-1', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'av-aip-1_copy'), os.path.join(aips_dir, 'av-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'bmac_av-placeholder1.txt'),
                    os.path.join(aip_path, 'objects', 'bmac_av-placeholder2.txt')]
        self.assertEqual(expected, result, "Problem with sort_av, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort_av, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort_av, log: MetadataError")

    def test_sort_av_dpx(self):
        """Test for an AV AIP from workflow dpx, which starts in a bag and has multiple sort and renaming patterns"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'bmac', 'dpx', 'coll-bmac', 'folder', 'av', 'av-aip-2', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'av-aip-2_copy'), os.path.join(aips_dir, 'av-aip-2'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'av-aip-2-dpx'),
                    os.path.join(aip_path, 'objects', 'av-aip-2-dpx', 'av-placeholder1.txt'),
                    os.path.join(aip_path, 'objects', 'av-aip-2-dpx', 'av-placeholder2.txt'),
                    os.path.join(aip_path, 'objects', 'av-aip-2-dpx', 'av-placeholder3.txt'),
                    os.path.join(aip_path, 'objects', 'placeholder-dpx.wav'),
                    os.path.join(aip_path, 'objects', 'placeholder.cue'),
                    os.path.join(aip_path, 'objects', 'placeholder.mov'),
                    os.path.join(aip_path, 'objects', 'placeholder2-dpx.wav'),
                    os.path.join(aip_path, 'objects', 'placeholder2.mov')]
        self.assertEqual(expected, result, "Problem with sort_av_dpx, AIP folder")

        # Test for contents of the movs-to-bag folder on staging.
        movs_path = os.path.join(staging_dir, 'movs-to-bag')
        result = make_directory_list(movs_path)
        expected = [os.path.join(movs_path, 'placeholder.mov'), os.path.join(movs_path, 'placeholder2.mov')]
        self.assertEqual(expected, result, "Problem with sort_av_dpx, MOVs folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort_av_dpx, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort_av_dpx, log: MetadataError")

    def test_sort_av_metadata(self):
        """Test for an AV AIP which contains files that go in the metadata subfolder"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'bmac', 'wav', 'coll-bmac', 'folder', 'av', 'av-aip-3', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'av-aip-3_copy'), os.path.join(aips_dir, 'av-aip-3'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'av-aip-3_files-deleted_2025-09-08_del.csv'),
                    os.path.join(aip_path, 'metadata', 'bmac_placeholder.framemd5'),
                    os.path.join(aip_path, 'metadata', 'bmac_placeholder.qctools.mkv'),
                    os.path.join(aip_path, 'metadata', 'bmac_placeholder.qctools.xml.gz'),
                    os.path.join(aip_path, 'metadata', 'bmac_placeholder.srt'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'bmac_av-placeholder.txt')]
        self.assertEqual(expected, result, "Problem with sort_av_metadata, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort_av_metadata, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort_av_metadata, log: MetadataError")

    def test_sort_av_mxf(self):
        """Test for an AV AIP from workflow mxf, which has a different renaming pattern"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'bmac', 'mxf', 'coll-bmac', 'folder', 'av', 'av-aip-4', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'av-aip-4_copy'), os.path.join(aips_dir, 'av-aip-4'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'bmac_wsb-video_av-placeholder.txt')]
        self.assertEqual(expected, result, "Problem with sort_av_mxf, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort_av_mxf, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort_av_mxf, log: MetadataError")

    def test_sort_emory(self):
        """Test for an AIP which contains an Emory metadata file, which goes in the metadata subfolder"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'emory', None, 'coll-emory', 'folder', 'general', 'emory-aip-1', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'emory-aip-1_copy'), os.path.join(aips_dir, 'emory-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'EmoryMD_Text.txt'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Test Dir'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'objects', 'Text 2.txt'),
                    os.path.join(aip_path, 'objects', 'Text.txt')]
        self.assertEqual(expected, result, "Problem with sort Emory metadata, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort Emory metadata, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort Emory metadata, log: MetadataError")

    def test_sort_files_deleted(self):
        """Test for an AIP which contains a deletion log, which goes in the metadata subfolder"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll-delete', 'folder', 'general', 'deletion-aip-1', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'deletion-aip-1_copy'), os.path.join(aips_dir, 'deletion-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'deletion-aip-1_files-deleted_2022-10-31_del.csv'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'Test Dir'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'objects', 'Text 2.txt'),
                    os.path.join(aip_path, 'objects', 'Text.txt')]
        self.assertEqual(expected, result, "Problem with sort files deleted log, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort files deleted log, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort files deleted log, log: MetadataError")

    def test_sort_none(self):
        """Test for an AIP with no metadata files (some would be metadata if AIP metadata was different)"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'dept', None, 'coll', 'folder', 'general', 'none-aip-1', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'none-aip-1_copy'), os.path.join(aips_dir, 'none-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'none-aip-1_coll.csv'),
                    os.path.join(aip_path, 'objects', 'Test Dir'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'none-aip-1.framemd5'),
                    os.path.join(aip_path, 'objects', 'Test Dir', 'Test Dir Text.txt'),
                    os.path.join(aip_path, 'objects', 'Text 2.txt'),
                    os.path.join(aip_path, 'objects', 'Text.txt')]
        self.assertEqual(expected, result, "Problem with sort none (no metadata), AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort none (no metadata), log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort none (no metadata), log: MetadataError")

    def test_sort_web(self):
        """Test for a web AIP (not MAGIL) with all the six Archive-It reports, which go in the metadata subfolder"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'magil', None, 'coll-web', 'folder', 'web', 'web-aip-1', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'web-aip-1_copy'), os.path.join(aips_dir, 'web-aip-1'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_coll.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_collscope.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_crawldef.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_crawljob.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_seed.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-1_seedscope.csv'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'warc-placeholder.txt')]
        self.assertEqual(expected, result, "Problem with sort web, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort web, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort web, log: MetadataError")

    def test_sort_web_magil(self):
        """Test for a MAGIL web AIP with four six Archive-It reports, which go in the metadata subfolder"""
        # Makes test input (AIP instance and AIP directory with files) and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'structure_directory')
        staging_dir = os.path.join(os.getcwd(), 'staging')
        aip = AIP(aips_dir, 'magil', None, 'coll-web', 'folder', 'web', 'web-aip-2', 'title', 1, 'InC', True)
        shutil.copytree(os.path.join(aips_dir, 'web-aip-2_copy'), os.path.join(aips_dir, 'web-aip-2'))
        structure_directory(aip, staging_dir)

        # Test for the contents of the AIP folder.
        aip_path = os.path.join(staging_dir, aips_dir, aip.id)
        result = make_directory_list(aip_path)
        expected = [os.path.join(aip_path, 'metadata'),
                    os.path.join(aip_path, 'metadata', 'web-aip-2_001_crawldef.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-2_002_crawldef.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-2_coll.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-2_crawljob.csv'),
                    os.path.join(aip_path, 'metadata', 'web-aip-2_seed.csv'),
                    os.path.join(aip_path, 'objects'),
                    os.path.join(aip_path, 'objects', 'warc1-placeholder.txt'),
                    os.path.join(aip_path, 'objects', 'warc2-placeholder.txt')]
        self.assertEqual(expected, result, "Problem with sort web_magil, AIP folder")

        # Test for the AIP log: ObjectsError.
        result = aip.log['ObjectsError']
        expected = 'Successfully created objects folder'
        self.assertEqual(expected, result, "Problem with sort web_magil, log: ObjectsError")

        # Test for the AIP log: MetadataError.
        result = aip.log['MetadataError']
        expected = 'Successfully created metadata folder'
        self.assertEqual(expected, result, "Problem with sort web_magil, log: MetadataError")




if __name__ == "__main__":
    unittest.main()
