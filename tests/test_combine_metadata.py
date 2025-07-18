"""Testing for the function combine_metadata, which takes an AIP class instance as input and
combines the FITS files in the AIP"s metadata folder into a single XML file."""

import os
import pandas as pd
import shutil
import unittest
import xml.etree.ElementTree as ET
from aip_functions import AIP, structure_directory, extract_metadata, combine_metadata


def read_xml(path):
    """
    Reads an XML file so that function about can be compared to the expected output (stored as a file in the repo).
    """
    with open(path, 'r') as result_file:
        read_file = result_file.read()
    return read_file


class TestCombineMetadata(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the log, errors folder, and combined fits xml, if present.
        """
        # Deletes files created by the function.
        file_paths = [os.path.join('combine_metadata', 'aip_log.csv'),
                      os.path.join('combine_metadata', 'multi_file', 'metadata', 'multi_file_combined-fits.xml'),
                      os.path.join('combine_metadata', 'one_file', 'metadata', 'one_file_combined-fits.xml')]
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

        # Deletes the errors folder and its contents.
        if os.path.exists('aips-with-errors'):
            shutil.rmtree('aips-with-errors')

    def test_one_file(self):
        """
        Test for an AIP with one file (Plain text).
        """
        # Makes the AIP instance and runs the function.
        aip_dir = os.path.join(os.getcwd(), 'combine_metadata')
        aip = AIP(aip_dir, "test", None, "coll-1", "one_file", "general", "one_file", "title", 1, True)
        combine_metadata(aip, os.getcwd())

        # Test for combined-fits.xml produced by the function.
        result = read_xml(os.path.join(aip_dir, "one_file", "metadata", "one_file_combined-fits.xml"))
        expected = read_xml(os.path.join(aip_dir, "expected_xml", "one_file_combined-fits.xml"))
        self.assertEqual(result, expected, "Problem with one file, combined-fits.xml")

        # Test for AIP log.
        result_log = aip.log["FITSError"]
        expected_log = "Successfully created combined-fits.xml"
        self.assertEqual(result_log, expected_log, "Problem with one file, log")

    def test_multiple_files(self):
        """
        Test for an AIP with multiple files of different formats (CSV, JSON, Plain text).
        """
        # Makes the AIP instance and runs the function.
        aip_dir = os.path.join(os.getcwd(), 'combine_metadata')
        aip = AIP(aip_dir, "test", None, "coll-1", "multi_file", "general", "multi_file", "title", 1, True)
        combine_metadata(aip, os.getcwd())

        # Test for combined-fits.xml produced by the function.
        result = read_xml(os.path.join(aip_dir, "multi_file", "metadata", "multi_file_combined-fits.xml"))
        expected = read_xml(os.path.join(aip_dir, "expected_xml", "multi_file_combined-fits.xml"))
        self.assertEqual(result, expected, "Problem with multiple files, combined-fits.xml")

        # Test for AIP log.
        result_log = aip.log["FITSError"]
        expected_log = "Successfully created combined-fits.xml"
        self.assertEqual(result_log, expected_log, "Problem with multiple files, log")

    def test_error_et_parse(self):
        """
        Test for an AIP where the FITS XML can"t be parsed correctly by ElementTree.
        Generates error by making a fake FITS file that is not real XML.
        """
        # Makes the AIP instance and runs the function.
        aip_dir = os.path.join(os.getcwd(), 'combine_metadata')
        aip = AIP(aip_dir, "test", None, "coll-1", "et_error", "general", "et_error", "title", 1, True)
        combine_metadata(aip, os.getcwd())

        # Test for if the folder is moved, both that it is in the error folder
        # and is not in the original location (AIPs directory).
        result = (os.path.exists(os.path.join("..", "errors", "combining_fits", "et_error")),
                  os.path.exists("et_error"))
        expected = (True, False)
        self.assertEqual(result, expected, "Problem with ET parse error, move to error folder")

        # Test for the AIP log, FITSError.
        result_log = aip.log["FITSError"]
        expected_log = "Issue when creating combined-fits.xml: syntax error: line 1, column 0"
        self.assertEqual(result_log, expected_log, "Problem with ET parse error, log: FITSError")

        # Test for the AIP log, Complete.
        result_log2 = aip.log["Complete"]
        expected_log2 = "Error during processing"
        self.assertEqual(result_log2, expected_log2, "Problem with ET parse error, log: Complete")


if __name__ == "__main__":
    unittest.main()
