"""Testing for the function organize_xml, which takes an AIP class instance as input and
deletes, copies, or moves the XML files created to produce the preservation.xml file."""

import fileinput
import unittest
from scripts.aip_functions import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """
        Makes an AIP instance and corresponding folder to use for testing.
        Includes running functions for the earlier workflow steps.
        """
        make_output_directories()

        self.aip = AIP(os.getcwd(), 'test', 'coll-1', 'aip-folder', 'aip-id', 'title', 1, True)
        os.mkdir(self.aip.id)
        with open(os.path.join(self.aip.id, 'file.txt'), 'w') as file:
            file.write("Test text")

        structure_directory(self.aip)
        extract_metadata(self.aip)
        combine_metadata(self.aip)
        make_cleaned_fits_xml(self.aip)
        make_preservation_xml(self.aip)
        validate_preservation_xml(self.aip)

    def tearDown(self):
        """
        If they are present, deletes the test AIP, the AIP log, the errors folder, and the script output folders.
        """

        if os.path.exists('aip-id'):
            shutil.rmtree('aip-id')

        log_path = os.path.join('..', 'aip_log.csv')
        if os.path.exists(log_path):
            os.remove(log_path)

        errors_path = os.path.join('..', 'errors')
        if os.path.exists(errors_path):
            shutil.rmtree(errors_path)

        script_output_folders = ('aips-to-ingest', 'fits-xml', 'preservation-xml')
        for folder in script_output_folders:
            path = os.path.join('..', folder)
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_organize_xml(self):
        """
        Test for organizing XML files after the preservation.xml file is made.
        Result for testing is a list of path tests for the XML files.
        """
        organize_xml(self.aip)

        result = [os.path.exists(os.path.join('..', 'preservation-xml', 'aip-id_preservation.xml')),
                  os.path.exists(os.path.join('aip-id', 'metadata', 'aip-id_preservation.xml')),
                  os.path.exists(os.path.join('..', 'fits-xml', 'aip-id_combined-fits.xml')),
                  os.path.exists(os.path.join('aip-id', 'metadata', 'aip-id_combined-fits.xml')),
                  os.path.exists(os.path.join('aip-id', 'metadata', 'aip-id_cleaned-fits.xml'))]

        expected = [True, True, True, False, False]

        self.assertEqual(result, expected, 'Problem with organize xml')


if __name__ == '__main__':
    unittest.main()
