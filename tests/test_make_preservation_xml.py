"""Testing for the function make_preservation_xml, which takes an AIP class instance as input and
makes the preservation.xml metadata file from the cleaned-fits.xml file already in the AIP metadata folder.
There is error handling throughout for XML transformation.

There is a test for each AIP ID format, since the stylesheet for making the preservation.xml
uses the ID to calculate additional values."""

import fileinput
import unittest
from scripts.aip_functions import *


def make_test_input(aip):
    """
    Makes a directory with a test file for the provided AIP instance
    and gets it ready for running the make_preservation_xml function.
    """

    # Makes the AIP folder and test files to use as the AIP content.
    # For a born-digital AIP (identifier contains er), makes two text files and a csv.
    os.mkdir(aip.id)
    if "er" in aip.id:
        with open(os.path.join(aip.id, "file.txt"), "w") as file:
            file.write("Test text")
        with open(os.path.join(aip.id, "file2.txt"), "w") as file2:
            file2.write("Test text" * 30)
        with open(os.path.join(aip.id, "file3.csv"), "w") as file3:
            file3.write("test,test,test,test,test\n")
            file3.write("test,test,test,test,test\n")
    # For a web AIP (currently the only other type using this script),
    # makes a file with a WARC extension.
    # Since it is not really a WARC, the format identification will be Unknown Binary.
    else:
        with open(os.path.join(aip.id, "file.warc"), "w") as file:
            file.write("Placeholder for a warc file")

    # Runs the functions for the earlier workflow steps so there is FITS data ready to make into a preservation.xml
    make_output_directories()
    structure_directory(aip)
    extract_metadata(aip)
    combine_metadata(aip)
    make_cleaned_fits_xml(aip)


def read_preservation_xml(aip_id):
    """
    Reads the preservation.xml produced by the test, replaces the UGA URI with default text uri,
    and returns the resulting string to use for testing if the function produced the correct XML.
    """
    xml_path = os.path.join(aip_id, "metadata", f"{aip_id}_preservation.xml")
    with fileinput.FileInput(xml_path, inplace=True) as file:
        for line in file:
            print(line.replace(c.NAMESPACE, "http://uri"), end="")
    with open(xml_path, "r") as open_xml:
        read_xml = open_xml.read()
    return read_xml


class MyTestCase(unittest.TestCase):

    def tearDown(self):
        """
        If they are present, deletes the test AIP and its contents,
        the AIP log, the errors folder, and the script output folders.
        """

        # Deletes any AIP folder, which would be in the current directory.
        aip_ids = ("error-id", "harg-0000-web-202108-0001", "harg-ms3786er0002", "harg-ms3786-web-202108-0001",
                   "har-ua20-002-web-202108-0001", "magil-ggp-2472041-2022-05", "rbrl-000-web-202102-0001",
                   "rbrl-025-er-000018", "rbrl-043-web-202102-0001")
        for aip_folder in aip_ids:
            if os.path.exists(aip_folder):
                shutil.rmtree(aip_folder)

        # Deletes the AIP log.
        if os.path.exists(os.path.join("..", "aip_log.csv")):
            os.remove(os.path.join("..", "aip_log.csv"))

        # Deletes the script output folders.
        for output_folder in ("aips-to-ingest", "errors", "fits-xml", "preservation-xml"):
            path = os.path.join("..", output_folder)
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_born_digital_hargrett(self):
        """
        Test for making the preservation.xml file for a Hargrett born-digital AIP.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "hargrett", "harg-ms3786", "harg-ms3786er0002", "harg-ms3786er0002",
                  "Hargrett Born-Digital Title", 1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for Hargrett born-digital")

    def test_born_digital_russell(self):
        """
        Test for making the preservation.xml file for a Russell born-digital AIP.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "russell", "rbrl-025", "rbrl-025-er-000018", "rbrl-025-er-000018",
                  "Russell Born-Digital Title", 1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for Russell born-digital")

    def test_error(self):
        """
        Test for error handling while making the preservation.xml file.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # causes the error by deleting the FITS file used as the saxon input, and runs the function.
        aip = AIP(os.getcwd(), "test", "coll-1", "error-folder", "error-id", "error title", 1, True)
        make_test_input(aip)
        os.remove(os.path.join("error-id", "metadata", "error-id_cleaned-fits.xml"))
        make_preservation_xml(aip)

        # Test for the AIP being moved to the error folder.
        # Tests that it is no longer in the AIP directory and is in the error folder.
        result = (os.path.exists(os.path.join("..", "errors", "pres_xml_saxon_error", "error-id")),
                  os.path.exists("error-id"))
        expected = (True, False)
        self.assertEqual(result, expected, "Problem with test for error handling, moving AIP folder")

        # Test for the AIP log.
        result_log = (aip.log["PresXML"], aip.log["Complete"])
        expected_log = ("Issue when creating preservation.xml. " 
                       "Saxon error: Source file error-id\\metadata\\error-id_cleaned-fits.xml does not exist\r\n",
                        "Error during processing")
        self.assertEqual(result_log, expected_log, "Problem with test for error handling")

    def test_web_hargrett(self):
        """
        Test for making the preservation.xml file for a Hargrett web AIP with no related collection.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "hargrett", "harg-0000", "harg-0000-web-202108-0001", "harg-0000-web-202108-0001",
                  "Hargrett Web Title: No Related Collection", 1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for Hargrett web, no collection")

    def test_web_hargrett_mms(self):
        """
        Test for making the preservation.xml file for a Hargrett web AIP with a related manuscript collection.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "hargrett", "harg-ms3786", "harg-ms3786-web-202108-0001", "harg-ms3786-web-202108-0001",
                  "Hargrett Web Title: Related Manuscript Collection", 1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for Hargrett web, manuscript collection")

    def test_web_hargrett_ua(self):
        """
        Test for making the preservation.xml file for Hargrett web AIP with a related university archives collection.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "hargrett", "har-ua20-002", "har-ua20-002-web-202108-0001",
                  "har-ua20-002-web-202108-0001", "Hargrett Web Title: Related University Archives Collection",
                  1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for Hargrett web, university archives collection")

    def test_web_magil(self):
        """
        Test for making the preservation.xml file for a MAGIL web AIP.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "magil", "magil-0000", "magil-ggp-2472041-2022-05", "magil-ggp-2472041-2022-05",
                  "MAGIL Web Title", 1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for MAGIL web")

    def test_web_russell(self):
        """
        Test for making the preservation.xml file for a Russell web AIP with no related collection.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "russell", "rbrl-000", "rbrl-000-web-202102-0001", "rbrl-000-web-202102-0001",
                  "Russell Web Title: No Related Collection", 1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for Russell web, no collection")

    def test_web_russell_collection(self):
        """
        Test for making a preservation.xml file for a Russell web AIP with a related collection.
        """
        # Makes the input needed for the function (AIP class instance and AIP folder with test files),
        # and runs the function.
        aip = AIP(os.getcwd(), "russell", "rbrl-043", "rbrl-043-web-202102-0001", "rbrl-043-web-202102-0001",
                  "Russell Web Title: Related Collection", 1, True)
        make_test_input(aip)
        make_preservation_xml(aip)

        # Test for the preservation.xml file.
        # The expected value is stored in the test folder of this script repo.
        result = read_preservation_xml(aip.id)
        with open(os.path.join("expected_xml", f"{aip.id}_preservation.xml"), "r") as expected_file:
            expected = expected_file.read()
        self.assertEqual(result, expected, "Problem with test for Russell web, collection")


if __name__ == "__main__":
    unittest.main()
