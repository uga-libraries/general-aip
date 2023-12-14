"""Testing for the function organize_xml, which takes an AIP class instance as input and
deletes, copies, or moves the XML files created to produce the preservation.xml file."""

import unittest
from aip_functions import *


class TestOrganizeXML(unittest.TestCase):

    def tearDown(self):
        """
        If they are present, deletes the test AIP, the AIP log, and the script output folders.
        """

        if os.path.exists("aip-id"):
            shutil.rmtree("aip-id")

        if os.path.exists("aip_log.csv"):
            os.remove("aip_log.csv")

        script_output_folders = ("aips-to-ingest", "fits-xml", "preservation-xml")
        for folder in script_output_folders:
            path = os.path.join("..", folder)
            if os.path.exists(path):
                shutil.rmtree(path)

    def test_organize_xml(self):
        """
        Test for organizing XML files after the preservation.xml file is made.
        """
        # Makes an AIP instance and corresponding AIP folder to use for testing.
        # To save times, makes placeholder files with the metadata filenames
        # instead of running the functions for the earlier steps of the script.
        make_output_directories()
        aip = AIP(os.getcwd(), "test", "coll-1", "aip-folder", "aip-id", "title", 1, True)
        os.makedirs(os.path.join("aip-id", "metadata"))
        with open(os.path.join("aip-id", "metadata", "aip-id_cleaned-fits.xml"), "w") as file:
            file.write("Cleaned FITS placeholder")
        with open(os.path.join("aip-id", "metadata", "aip-id_combined-fits.xml"), "w") as file:
            file.write("Combined FITS placeholder")
        with open(os.path.join("aip-id", "metadata", "aip-id_preservation.xml"), "w") as file:
            file.write("Preservation XML placeholder")
        os.makedirs(os.path.join("aip-id", "objects"))
        with open(os.path.join("aip-id", "objects", "file.txt"), "w") as file:
            file.write("Test text")

        # Runs the function being tested.
        organize_xml(aip)

        # Tests if the files are at the original location and in the new location (if copied or moved).
        # and compares the result to what is expected.
        result = [os.path.exists(os.path.join("..", "preservation-xml", "aip-id_preservation.xml")),
                  os.path.exists(os.path.join("aip-id", "metadata", "aip-id_preservation.xml")),
                  os.path.exists(os.path.join("..", "fits-xml", "aip-id_combined-fits.xml")),
                  os.path.exists(os.path.join("aip-id", "metadata", "aip-id_combined-fits.xml")),
                  os.path.exists(os.path.join("aip-id", "metadata", "aip-id_cleaned-fits.xml"))]
        expected = [True, True, True, False, False]
        self.assertEqual(result, expected, "Problem with organize xml")


if __name__ == "__main__":
    unittest.main()
