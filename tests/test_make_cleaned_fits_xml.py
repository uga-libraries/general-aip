"""Testing for the function make_cleaned_fits_xml, which takes an AIP class instance as input and
makes a simplified version of the combined-fits.xml file already in the metadata folder.
There is error handling for the XML transformation."""
import os
import shutil
import unittest
from aip_functions import AIP, make_cleaned_fits_xml
from test_combine_metadata import read_xml


class TestMakeCleanedFitsXML(unittest.TestCase):

    def tearDown(self):
        """If they are present, deletes the script outputs."""
        # Deletes the cleaned-fits.xml file from the successful test.
        xml_path = os.path.join(os.getcwd(), 'make_cleaned_fits_xml', 'aip1', 'metadata', 'aip1_cleaned-fits.xml')
        if os.path.exists(xml_path):
            os.remove(xml_path)

        # Deletes the aip_log, errors folder, and aip folder from the error test.
        log_path = os.path.join(os.path.join(os.getcwd(), 'make_cleaned_fits_xml', 'aip_log.csv'))
        if os.path.exists(log_path):
            os.remove(log_path)

        errors_path = os.path.join(os.getcwd(), 'aip_staging_location', 'aips-with-errors')
        if os.path.exists(errors_path):
            shutil.rmtree(errors_path)

        aip_path = os.path.join(os.getcwd(), 'make_cleaned_fits_xml', 'aip0')
        if os.path.exists(aip_path):
            shutil.rmtree(aip_path)

    def test_correct(self):
        """Test for successfully making the cleaned-fits.xml file."""
        # Makes the input variables and runs the function being tested.
        aip_dir = os.path.join(os.getcwd(), 'make_cleaned_fits_xml')
        staging_dir = os.path.join(os.getcwd(), 'aip_staging_location')
        aip = AIP(aip_dir, 'dept', None, 'coll-1', 'aip_folder', 'general', 'aip1', 'title', '1', 'zip')
        make_cleaned_fits_xml(aip, staging_dir)

        # Compares the cleaned-fits.xml file produced by the function to a xml file with the expected values.
        result = read_xml(os.path.join(aip_dir, 'aip1', 'metadata', 'aip1_cleaned-fits.xml'))
        expected = read_xml(os.path.join(aip_dir, 'aip1_cleaned-fits_expected.xml'))
        self.assertEqual(result, expected, "Problem with correct")

    # def test_error(self):
    #     """
    #     Test for error handling while making the cleaned-fits.xml file.
    #     """
    #     # Causes the error by deleting the combined-fits.xml file used as the saxon input.
    #     os.remove(os.path.join("aip-id", "metadata", "aip-id_combined-fits.xml"))
    #     make_cleaned_fits_xml(self.aip)
    #
    #     # Test for if the folder is moved, both that it is in the error folder
    #     # and is not in the original location (AIPs directory).
    #     result = (os.path.exists(os.path.join("..", "errors", "cleaned_fits_saxon_error", "aip-id")),
    #               os.path.exists("aip-id"))
    #     expected = (True, False)
    #     self.assertEqual(result, expected, "Problem with cleaned fits error handling, move to error folder")
    #
    #     # Test for the AIP log, PresXML.
    #     result_log = self.aip.log["PresXML"]
    #     expected_log = "Issue when creating cleaned-fits.xml. " \
    #                    "Saxon error: Source file aip-id\\metadata\\aip-id_combined-fits.xml does not exist\r\n"
    #     self.assertEqual(result_log, expected_log, "Problem with cleaned fits error handling, log: PresXML")
    #
    #     # Test for the AIP log, Complete.
    #     result_log2 = self.aip.log["Complete"]
    #     expected_log2 = "Error during processing"
    #     self.assertEqual(result_log2, expected_log2, "Problem with cleaned fits error handling, log: Complete")


if __name__ == "__main__":
    unittest.main()
