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
        Deletes the log, errors folder, and AIP test folders, if present.
        """
        if os.path.exists(os.path.join("..", "aip_log.csv")):
            os.remove(os.path.join("..", "aip_log.csv"))

        directory_paths = (os.path.join("..", "errors"), "one_file", "multi_file", "et_error")
        for directory_path in directory_paths:
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)

    def test_one_file(self):
        """
        Test for an AIP with one file.
        """
        # Makes the test AIP, including making the initial AIP instance, folder and file and
        # running the first functions for the AIP workflow.
        aip = AIP(os.getcwd(), "test", "coll-1", "one_file", "one_file", "title", 1, True)
        os.mkdir("one_file")
        with open(os.path.join("one_file", "Text.txt"), "w") as file:
            file.write("Test File")
        structure_directory(aip)
        extract_metadata(aip)
        combine_metadata(aip)

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
        # Makes the test AIP, including making the initial AIP instance, folders and files and
        # running the first two functions for the AIP workflow.
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
        combine_metadata(aip)

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
        # Makes the test AIP, including making the initial AIP instance, folder and file and
        # running the first function for the AIP workflow.
        aip = AIP(os.getcwd(), "test", "coll-1", "et_error", "et_error", "title", 1, True)
        os.mkdir("et_error")
        with open(os.path.join("et_error", "Text.txt"), "w") as file:
            file.write("Test File")
        structure_directory(aip)

        # To generate the error, adds a text file instead of the correct fits.xml file
        # that would be generated by the extract_metadata_only function.
        with open(os.path.join("et_error", "metadata", "et_error_fits.xml"), "w") as file:
            file.write("This is not FITS XML")

        # Runs the function with the error handling being tested.
        combine_metadata(aip)

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
