"""Testing for the function make_cleaned_fits_xml, which takes an AIP class instance as input and
makes a simplified version of the combined-fits.xml file already in the metadata folder.
There is error handling for the XML transformation."""

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

    def test_make_cleaned_fits_xml(self):
        """
        Test for successfully making the cleaned-fits.xml file.
        Result for testing is the contents of the cleaned-fits.xml file.
        """
        make_cleaned_fits_xml(self.aip)

        # Edits the timestamp and filepath to consistent values to allow an exact comparison to expected.
        tree = ET.parse(os.path.join('aip-id', 'metadata', 'aip-id_cleaned-fits.xml'))
        root = tree.getroot()
        for fits in root.iter('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fits'):
            fits.set('timestamp', '01/01/22 1:23 PM')
        for filepath in root.iter('{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}filepath'):
            filepath.text = 'C:/Path/aip-id/objects/file.txt'
        tree.write(os.path.join('aip-id', 'metadata', 'aip-id_cleaned-fits.xml'),
                   xml_declaration=True, encoding='UTF-8')

        # Reads the cleaned-fits.xml file produced by the function and a cleaned-fits.xml file with the expected values.
        with open(os.path.join('aip-id', 'metadata', 'aip-id_cleaned-fits.xml'), 'r') as result_file:
            result = result_file.read()
        with open(os.path.join('expected_xml', 'aip-id_cleaned-fits.xml'), 'r') as expected_file:
            expected = expected_file.read()

        self.assertEqual(result, expected, 'Problem with cleaned fits')

    def test_make_cleaned_fits_xml_error(self):
        """
        Test for error handling while making the cleaned-fits.xml file.
        Result for testing is the AIP log.
        """
        # Causes the error by deleting the combined-fits.xml file used as the saxon input.
        os.remove(os.path.join('aip-id', 'metadata', 'aip-id_combined-fits.xml'))
        make_cleaned_fits_xml(self.aip)

        result = self.aip.log['PresXML']

        expected = 'Issue when creating cleaned-fits.xml. ' \
                   'Saxon error: Source file aip-id\\metadata\\aip-id_combined-fits.xml does not exist\r\n'

        self.assertEqual(result, expected, 'Problem with cleaned fits error handling')


if __name__ == '__main__':
    unittest.main()
