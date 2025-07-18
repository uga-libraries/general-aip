"""Testing for the function extract_metadata, which takes an AIP class instance as input and
uses FITS to extract technical metadata."""

import os
import pandas as pd
import shutil
import unittest
from aip_functions import AIP, structure_directory, extract_metadata


class TestExtractMetadata(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the FITS error log and FITS files in the metadata folders, if present.
        """
        aips_directory = os.path.join(os.getcwd(), 'extract_metadata')
        file_paths = [os.path.join(aips_directory, 'aip-id-error', 'metadata', 'aip-id-error_fits-tool-errors_fitserr.txt'),
                      os.path.join(aips_directory, 'aip-id-error', 'metadata', 'not.xml_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-multi', 'metadata', 'output.csv_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-multi', 'metadata', 'output.json_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-multi', 'metadata', 'Text.txt_fits.xml'),
                      os.path.join(aips_directory, 'aip-id-one', 'metadata', 'Text.txt_fits.xml')]
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_one_file(self):
        """
        Test for an AIP with one file.
        """
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'extract_metadata')
        aip = AIP(aips_dir, "dept", None, "coll-1", "one_folder", "general", "aip-id-one", "title", 1, True)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        result = os.listdir(os.path.join(aips_dir, "aip-id-one", "metadata"))
        expected = ["metadata.txt", "Text.txt_fits.xml"]
        self.assertEqual(result, expected, "Problem with one file, metadata folder")

        # Test for the AIP log.
        result_log = aip.log["FITSTool"]
        expected_log = "No FITS tools errors"
        self.assertEqual(result_log, expected_log, "Problem with one file, log")

    def test_multiple_files(self):
        """
        Test for an AIP with multiple files of different formats (CSV, JSON, Plain text).
        """
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'extract_metadata')
        aip = AIP(aips_dir, "dept", None, "coll-1", "multi_folder", "general", "aip-id-multi", "title", 1, True)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        result = os.listdir(os.path.join(aips_dir, "aip-id-multi", "metadata"))
        expected = ["metadata.txt", "output.csv_fits.xml", "output.json_fits.xml", "Text.txt_fits.xml"]
        self.assertEqual(result, expected, "Problem with multiple files, metadata folder")

        # Test for the AIP log.
        result_log = aip.log["FITSTool"]
        expected_log = "No FITS tools errors"
        self.assertEqual(result_log, expected_log, "Problem with multiple files, log")

    def test_error_fits_tool(self):
        """
        Test for an AIP with a format that causes FITS to generate an error (text file with XML extension).
        """
        # Makes test input and runs the function being tested.
        aips_dir = os.path.join(os.getcwd(), 'extract_metadata')
        aip = AIP(aips_dir, "dept", None, "coll-1", "tool_error_folder", "general", "aip-id-error", "title", 1, True)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        result = os.listdir(os.path.join(aips_dir, "aip-id-error", "metadata"))
        expected = ["aip-id-error_fits-tool-errors_fitserr.txt", "metadata.txt", "not.xml_fits.xml"]
        self.assertEqual(result, expected, "Problem with error, metadata folder")

        # Test for the FITS error log, which is if 3 phrases are in the file.
        # The contents of the entire file cannot be tested, since most are variable (timestamps and file paths).
        with open(os.path.join(aips_dir, "aip-id-error", "metadata", "aip-id-error_fits-tool-errors_fitserr.txt")) as file:
            content = file.read()
            result = ("org.jdom.input.JDOMParseException" in content,
                      "Tool error processing file" in content,
                      "Content is not allowed in prolog." in content)
        expected = (True, True, True)
        self.assertEqual(result, expected, "Problem with error, FITS tool log")

        # Test for the AIP log.
        result_log = aip.log["FITSTool"]
        expected_log = "FITS tools generated errors (saved to metadata folder)"
        self.assertEqual(result_log, expected_log, "Problem with error, AIP log")


if __name__ == "__main__":
    unittest.main()
