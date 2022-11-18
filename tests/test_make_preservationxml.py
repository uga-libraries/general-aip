"""Testing for the function make_preservationxml, which takes an AIP class instance as input and
makes the preservation.xml metadata file.
There is error handling throughout for XML transformations and validating the preservation.xml.
There are four functions used, to keep each step separate."""

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
        Temporarily using if the file exists to test the result.
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
        Test for error handling while making the cleaned-fits.xml file
        by deleting the combined-fits.xml file used as the saxon input.
        The AIP log is used to test the result.
        """
        os.remove(os.path.join('aip-id', 'metadata', 'aip-id_combined-fits.xml'))
        make_cleaned_fits_xml(self.aip)
        result = self.aip.log['PresXML']
        expected = 'Issue when creating cleaned-fits.xml. ' \
                   'Saxon error: Source file aip-id\\metadata\\aip-id_combined-fits.xml does not exist\r\n'
        self.assertEqual(result, expected, 'Problem with cleaned fits error handling')

    def test_make_preservation_xml(self):
        """
        Test for successfully making the preservation.xml file.
        The contents of the preservation.xml to test the result.
        """
        make_cleaned_fits_xml(self.aip)
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
        Test for error handling while making the preservation.xml file
        by not making the cleaned-fits.xml file used as the saxon input.
        The AIP log is used to test the result.
        """
        make_preservation_xml(self.aip)
        result = self.aip.log['PresXML']
        expected = 'Issue when creating preservation.xml. ' \
                   'Saxon error: Source file aip-id\\metadata\\aip-id_cleaned-fits.xml does not exist\r\n'
        self.assertEqual(result, expected, 'Problem with preservation.xml error handling')

    def test_validate_preservation_xml(self):
        """
        Test for successfully validating the preservation.xml file.
        The AIP log is used to test the result.
        """
        make_cleaned_fits_xml(self.aip)
        make_preservation_xml(self.aip)
        validate_preservation_xml(self.aip)
        result = self.aip.log['PresValid']
        expected = f'Preservation.xml valid on {datetime.date.today()}'
        # Since the log for preservation.xml validation includes a timestamp, assert cannot require an exact match.
        self.assertIn(expected, result, 'Problem with preservation.xml validating')

    def test_validate_preservation_xml_missing(self):
        """
        Test for error handling if the preservation.xml file is missing during validation.
        The AIP log is used to test the result.
        """
        make_cleaned_fits_xml(self.aip)
        validate_preservation_xml(self.aip)
        result = self.aip.log['PresXML']
        expected = 'Preservation.xml was not created. xmllint error: ' \
                   'warning: failed to load external entity "aip-id/metadata/aip-id_preservation.xml"\r\n'
        self.assertEqual(result, expected, 'Problem with error handling of missing preservation.xml')

    def test_validate_preservation_xml_error(self):
        """
        Test for error handling if the preservation.xml file is not valid.
        The contents of the validation log are used to test the result.
        """
        make_cleaned_fits_xml(self.aip)
        make_preservation_xml(self.aip)

        # Edits the preservation.xml to remove the required field <dc:title>, which is the first element.
        ET.register_namespace('dc', 'http://purl.org/dc/terms/')
        ET.register_namespace('premis', 'http://www.loc.gov/premis/v3')
        tree = ET.parse(os.path.join('aip-id', 'metadata', 'aip-id_preservation.xml'))
        root = tree.getroot()
        root.remove(root[0])
        tree.write(os.path.join('aip-id', 'metadata', 'aip-id_preservation.xml'))

        validate_preservation_xml(self.aip)
        with open(os.path.join('..', 'errors', 'preservationxml_not_valid', 'aip-id_presxml_validation.txt'), 'r') as f:
            result = f.readlines()
        expected = ["Element '{http://purl.org/dc/terms/}rights': This element is not expected. Expected is ( {http://purl.org/dc/terms/}title ).\n",
                    "\n", "aip-id/metadata/aip-id_preservation.xml fails to validate\n", "\n", "\n"]
        self.assertEqual(result, expected, 'Problem with error handling of preservation.xml file that is not valid')

    def test_organize_xml(self):
        """
        Test for organizing XML files after the preservation.xml file is made.
        A list of path tests for the XML files is used to test the result.
        """
        make_cleaned_fits_xml(self.aip)
        make_preservation_xml(self.aip)
        validate_preservation_xml(self.aip)
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
