"""Testing for the function combine_metadata, which takes an AIP class instance as input and
combines the FITS files in the AIP"s metadata folder into a single XML file."""

import os
import pandas as pd
import shutil
import unittest
import xml.etree.ElementTree as ET
from aip_functions import AIP, structure_directory, extract_metadata, combine_metadata


def update_fits(path):
    """
    Reads the FITS XML and edits the data to remove data that varies each time the test is run
    so that it can be compared to expected results.
    Saves the updated XML so it can later be read and compared to another file with the expected results.
    """

    # Reads data from XML produced by the function.
    tree = ET.parse(path)
    root = tree.getroot()

    # Changes the timestamp attribute of every fits element.
    for fits in root.iter("{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fits"):
        fits.set("timestamp", "VARIES")

    # Changes the beginning of the filepath of every filepath element.
    for filepath in root.iter("{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}filepath"):
        new_path = filepath.text.replace(os.getcwd(), "CURRENT-DIRECTORY")
        filepath.text = new_path

    # Changes the value of every fslastmodified element.
    for date in root.iter("{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}fslastmodified"):
        date.text = "0000000000000"

    # Changes the fitsExecutionTime attribute of every statistics element.
    for stats in root.iter("{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}statistics"):
        stats.set("fitsExecutionTime", "000")

    # Changes the executionTime attribute of every tool element with that attribute.
    for tool in root.iter("{http://hul.harvard.edu/ois/xml/ns/fits/fits_output}tool"):
        if "executionTime" in tool.attrib:
            tool.set("executionTime", "000")

    # Saves the changes to the combined-fits.xml file.
    tree.write(path, xml_declaration=True, encoding="UTF-8")

    # Reads and returns the value of reading the combined-fits.xml file.
    with open(path, "r") as result_file:
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
        Test for an AIP with one file.
        """
        # Makes the AIP instance and runs the function.
        aip_dir = os.path.join(os.getcwd(), 'combine_metadata')
        aip = AIP(aip_dir, "test", None, "coll-1", "one_file", "general", "one_file", "title", 1, True)
        combine_metadata(aip, os.getcwd())

        # Test for combined-fits.xml produced by the function.
        result = update_fits(os.path.join("one_file", "metadata", "one_file_combined-fits.xml"))
        with open(os.path.join("expected_xml", "one_file_combined-fits.xml")) as expected_file:
            expected = expected_file.read()
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
        result = update_fits(os.path.join("multi_file", "metadata", "multi_file_combined-fits.xml"))
        with open(os.path.join("expected_xml", "multi_file_combined-fits.xml")) as expected_file:
            expected = expected_file.read()
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
