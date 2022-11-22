"""Testing for the function make_preservation_xml, which takes an AIP class instance as input and
makes the preservation.xml metadata file from the cleaned-fits.xml file already in the AIP metadata folder.
There is error handling throughout for XML transformation."""

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

    def test_make_preservation_xml(self):
        """
        Test for successfully making the preservation.xml file.
        Result for testing is the contents of the preservation.xml file.
        """
        make_preservation_xml(self.aip)

        # Replaces the UGA URI throughout the preservation.xml with "uri", since it cannot be in GitHub.
        with fileinput.FileInput(os.path.join('aip-id', 'metadata', 'aip-id_preservation.xml'), inplace=True) as file:
            for line in file:
                print(line.replace(c.NAMESPACE, 'http://uri'), end="")

        # Reads the preservation.xml file produced by the function and a preservation.xml file with the expected values.
        with open(os.path.join('aip-id', 'metadata', 'aip-id_preservation.xml'), 'r') as result_file:
            result = result_file.read()
        with open(os.path.join('expected_xml', 'aip-id_preservation.xml'), 'r') as expected_file:
            expected = expected_file.read()

        self.assertEqual(result, expected, 'Problem with preservation.xml')

    def test_make_preservation_xml_error(self):
        """
        Test for error handling while making the preservation.xml file.
        Result for testing is the AIP log.
        """
        # Causes the error by deleting the cleaned-fits.xml file used as the saxon input.
        os.remove(os.path.join('aip-id', 'metadata', 'aip-id_cleaned-fits.xml'))

        make_preservation_xml(self.aip)

        result = self.aip.log['PresXML']

        expected = 'Issue when creating preservation.xml. ' \
                   'Saxon error: Source file aip-id\\metadata\\aip-id_cleaned-fits.xml does not exist\r\n'

        self.assertEqual(result, expected, 'Problem with preservation.xml error handling')


if __name__ == '__main__':
    unittest.main()
