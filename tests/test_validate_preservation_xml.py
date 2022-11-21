"""Testing for the function validate_preservation_xml, which takes an AIP class instance as input and
validates the preservation.xml metadata file already in the AIP metadata folder.
There is error handling for if the preservation.xml file is missing or not valid."""

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
        make_cleaned_fits_xml(self.aip)
        make_preservation_xml(self.aip)

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

    def test_validate_preservation_xml(self):
        """
        Test for successfully validating the preservation.xml file.
        The result for testing is the AIP log.
        """
        validate_preservation_xml(self.aip)
        result = self.aip.log['PresValid']
        expected = f'Preservation.xml valid on {datetime.date.today()}'
        # Since the log for preservation.xml validation includes a timestamp, assert cannot require an exact match.
        self.assertIn(expected, result, 'Problem with preservation.xml validating')

    def test_validate_preservation_xml_missing(self):
        """
        Test for error handling if the preservation.xml file is missing during validation.
        The result for testing is the AIP log.
        """
        # Causes the error by deleting the preservation.xml file.
        os.remove(os.path.join('aip-id', 'metadata', 'aip-id_preservation.xml'))
        validate_preservation_xml(self.aip)

        result = self.aip.log['PresXML']

        expected = 'Preservation.xml was not created. xmllint error: ' \
                   'warning: failed to load external entity "aip-id/metadata/aip-id_preservation.xml"\r\n'

        self.assertEqual(result, expected, 'Problem with error handling of missing preservation.xml')

    def test_validate_preservation_xml_error(self):
        """
        Test for error handling if the preservation.xml file is not valid.
        Result for testing is the contents of the validation log.
        """
        # Causes the error by removing the field <dc:title> (the first element) from the preservation.xml.
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


if __name__ == '__main__':
    unittest.main()
