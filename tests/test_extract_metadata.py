"""Testing for the function extract_metadata, which takes an AIP class instance as input and
uses FITS to extract technical metadata."""

import os
import pandas as pd
import shutil
import unittest
from scripts.aip_functions import AIP, structure_directory, extract_metadata


class TestExtractMetadata(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the log, error folder, and AIP test folders, if present.
        """
        if os.path.exists(os.path.join("..", "aip_log.csv")):
            os.remove(os.path.join("..", "aip_log.csv"))
        
        directory_paths = (os.path.join("..", "errors"), "one_file", "multi_file", "tool_error")
        for directory_path in directory_paths:
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)

    def test_one_file(self):
        """
        Test for an AIP with one file.
        """
        aip = AIP(os.getcwd(), "test", "coll-1", "one_file", "one_file", "title", 1, True)
        os.mkdir("one_file")
        with open(os.path.join("one_file", "Text.txt"), "w") as file:
            file.write("Test File")
        structure_directory(aip)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        result = os.listdir(os.path.join("one_file", "metadata"))
        expected = ["Text.txt_fits.xml"]
        self.assertEqual(result, expected, "Problem with one file, metadata folder")

        # Test for the AIP log.
        result_log = aip.log["FITSTool"]
        expected_log = "No FITS tools errors"
        self.assertEqual(result_log, expected_log, "Problem with one file, log")

    def test_multiple_files(self):
        """
        Test for an AIP with multiple files of different formats (CSV, JSON, Plain text).
        """
        aip = AIP(os.getcwd(), "test", "coll-1", "multi_file", "multi_file", "title", 1, True)
        os.mkdir("multi_file")
        with open(os.path.join("multi_file", "Text.txt"), "w") as file:
            file.write("Test File")
        os.mkdir(os.path.join("multi_file", "Pandas Output"))
        df = pd.DataFrame({"First": ["a", "b", "c", "d"], "Second": [1, 2, 3, 4], "Third": [0.1, 0.2, 0.3, 0.4]})
        df.to_csv(os.path.join("multi_file", "Pandas Output", "output.csv"), index=False)
        df.to_json(os.path.join("multi_file", "Pandas Output", "output.json"))
        structure_directory(aip)
        extract_metadata(aip)

        # Test for the contents of the metadata folder.
        result = os.listdir(os.path.join("multi_file", "metadata"))
        expected = ["output.csv_fits.xml", "output.json_fits.xml", "Text.txt_fits.xml"]
        self.assertEqual(result, expected, "Problem with multiple files, metadata folder")

        # Test for the AIP log.
        result_log = aip.log["FITSTool"]
        expected_log = "No FITS tools errors"
        self.assertEqual(result_log, expected_log, "Problem with multiple files, log")

    def test_error_fits_tool(self):
        """
        Test for an AIP with a format that causes FITS to generate an error.
        """
        # Makes the test AIP, including making the initial AIP instance, folder and file and
        # running the first two functions for the AIP workflow.
        # Generates error by making a text file with an XML extension.
        aip = AIP(os.getcwd(), "test", "coll-1", "tool_error", "tool_error", "title", 1, True)
        os.mkdir("tool_error")
        with open(os.path.join("tool_error", "not.xml"), "w") as file:
            file.write("This is not XML")
        structure_directory(aip)
        extract_metadata(aip)

        # Test for the FITS error log, which is if 3 phrases are in the file.
        # The contents of the entire file cannot be tested, since most are variable (timestamps and file paths).
        with open(os.path.join("tool_error", "metadata", "tool_error_fits-tool-errors_fitserr.txt")) as file:
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
