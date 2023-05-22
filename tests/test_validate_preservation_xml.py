"""Testing for the function validate_preservation_xml, which takes an AIP class instance as input and
validates the preservation.xml metadata file already in the AIP metadata folder.
There is error handling for if the preservation.xml file is missing or not valid."""

import unittest
from scripts.aip_functions import *


class TestValidatePreservationXML(unittest.TestCase):

    def setUp(self):
        """
        Makes an AIP instance and corresponding folder to use for testing.
        Includes running functions for the earlier workflow steps.
        """
        make_output_directories()

        self.aip = AIP(os.getcwd(), "test", "coll-1", "aip-folder", "aip-id", "title", 1, True)
        os.mkdir(self.aip.id)
        with open(os.path.join(self.aip.id, "file.txt"), "w") as file:
            file.write("Test text")

        structure_directory(self.aip)
        extract_metadata(self.aip)
        combine_metadata(self.aip)
        make_cleaned_fits_xml(self.aip)
        make_preservation_xml(self.aip)

    def tearDown(self):
        """
        If they are present, deletes the test AIP, the AIP log, the errors folder, and the script output folders.
        """

        if os.path.exists("aip-id"):
            shutil.rmtree("aip-id")

        log_path = os.path.join("..", "aip_log.csv")
        if os.path.exists(log_path):
            os.remove(log_path)

        errors_path = os.path.join("..", "errors")
        if os.path.exists(errors_path):
            shutil.rmtree(errors_path)

        script_output_folders = ("aips-to-ingest", "fits-xml", "preservation-xml")
        for folder in script_output_folders:
            path = os.path.join("..", folder)
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_valid(self):
        """
        Test for successfully validating the preservation.xml file.
        """
        # Runs the function being tested.
        validate_preservation_xml(self.aip)

        # Test for the AIP Log: preservation.xml is made.
        result_presxml = self.aip.log["PresXML"]
        expected_presxml = "Successfully created preservation.xml"
        self.assertEqual(result_presxml, expected_presxml, "Problem with valid, log: PresXML")

        # Test for the AIP Log: preservation.xml is valid.
        # Removes the timestamp (last 16 characters) from result for a consistent expected value.
        result_valid = self.aip.log["PresValid"][:-16]
        expected_valid = f"Preservation.xml valid on {datetime.date.today()}"
        self.assertEqual(result_valid, expected_valid, "Problem with valid, log: PresValid")

    def test_error_missing(self):
        """
        Test for error handling if the preservation.xml file is missing during validation.
        """
        # Causes the error by deleting the preservation.xml file and then runs the function being tested.
        os.remove(os.path.join("aip-id", "metadata", "aip-id_preservation.xml"))
        validate_preservation_xml(self.aip)

        # Test for folder is moved, both that it is not in the original location and is in the error folder.
        in_original = os.path.exists("aip-id")
        in_error = os.path.exists(os.path.join("..", "errors", "preservationxml_not_found", "aip-id"))
        result = (in_original, in_error)
        expected = (False, True)
        self.assertEqual(result, expected, "Problem with error: missing, move to error folder")

        # Test for the AIP Log: preservation.xml is made.
        result_presxml = self.aip.log["PresXML"]
        expected_presxml = 'Preservation.xml was not created. xmllint error: ' \
                           'warning: failed to load external entity "aip-id/metadata/aip-id_preservation.xml"\r\n'
        self.assertEqual(result_presxml, expected_presxml, "Problem with error: missing, log: PresXML")

        # Test for the AIP Log: preservation.xml is valid.
        result_presvalid = self.aip.log["PresValid"]
        expected_presvalid = "n/a"
        self.assertEqual(result_presvalid, expected_presvalid, "Problem with error: missing, log: PresValid")

        # Test for the AIP Log: Complete.
        result_complete = self.aip.log["Complete"]
        expected_complete = "Error during processing"
        self.assertEqual(result_complete, expected_complete, "Problem with error: missing, log: Complete")

    def test_error_not_valid(self):
        """
        Test for error handling if the preservation.xml file is not valid.
        Result for testing is the contents of the validation log, plus the AIP log.
        """
        # Causes the error by removing the field <dc:title> (the first element) from the preservation.xml.
        ET.register_namespace("dc", "http://purl.org/dc/terms/")
        ET.register_namespace("premis", "http://www.loc.gov/premis/v3")
        tree = ET.parse(os.path.join("aip-id", "metadata", "aip-id_preservation.xml"))
        root = tree.getroot()
        root.remove(root[0])
        tree.write(os.path.join("aip-id", "metadata", "aip-id_preservation.xml"))

        # Runs the function being tested.
        validate_preservation_xml(self.aip)

        # Test for folder is moved, both that it is not in the original location and is in the error folder.
        in_original = os.path.exists("aip-id")
        in_error = os.path.exists(os.path.join("..", "errors", "preservationxml_not_valid", "aip-id"))
        result = (in_original, in_error)
        expected = (False, True)
        self.assertEqual(result, expected, "Problem with error: not valid, move to error folder")

        # Test for the validation log.
        with open(os.path.join("..", "errors", "preservationxml_not_valid", "aip-id_presxml_validation.txt"), "r") as f:
            result_log = f.readlines()
        expected_log = ["Element '{http://purl.org/dc/terms/}rights': This element is not expected. " 
                        'Expected is ( {http://purl.org/dc/terms/}title ).\n',
                        '\n', 'aip-id\\metadata\\aip-id_preservation.xml fails to validate\n', '\n', '\n']
        self.assertEqual(result_log, expected_log, "Problem with error: not valid, validation log")

        # Test for the AIP Log: preservation.xml is made.
        result_presxml = self.aip.log["PresXML"]
        expected_presxml = "Successfully created preservation.xml"
        self.assertEqual(result_presxml, expected_presxml, "Problem with error: not valid, log: PresXML")

        # Test for the AIP Log: preservation.xml is valid.
        result_presvalid = self.aip.log["PresValid"]
        expected_presvalid = "Preservation.xml is not valid (see log in error folder)"
        self.assertEqual(result_presvalid, expected_presvalid, "Problem with error: not valid, log: PresValid")

        # Test for the AIP Log: Complete.
        result_complete = self.aip.log["Complete"]
        expected_complete = "Error during processing"
        self.assertEqual(result_complete, expected_complete, "Problem with error: not valid, log: Complete")


if __name__ == "__main__":
    unittest.main()
