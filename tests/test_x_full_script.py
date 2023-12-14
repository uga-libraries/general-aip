"""
Testing for the entire script, with input that represents the different workflows that use the script.
It does not currently include tests for error handling.
"""

import csv
import datetime
import os
import re
import shutil
import subprocess
import unittest


def path_list(dir_name):
    """
    Makes and returns a list of the paths of every file and folder in a directory.
    Paths are relative, starting with the provided directory.
    """
    paths_list = []

    # Navigates all levels in the AIPs directory.
    for root, dirs, files in os.walk(dir_name):

        # Adds the path for every folder.
        for directory in dirs:
            paths_list.append(os.path.join(root, directory))

        # Adds the path for every file.
        # Makes changes to create consistent data for comparison to the expected.
        for file in files:

            # Edits the file size that is part of zipped AIP filenames, since that varies each time.
            if root.endswith("aips-to-ingest") and file.endswith(".tar.bz2"):
                file = re.sub(r"_bag.\d+.", "_bag.1000.", file)

            # Skips the FITS tool error log because FITS does not always have a tool error on the test files.
            # Adds all other files to the list.
            if file.endswith("_fits-tool-errors_fitserr.txt"):
                continue
            paths_list.append(os.path.join(root, file))

    return paths_list


def log_list(log_path):
    """
    Reads the aip_log.csv file and returns a list of the rows in the log.
    """
    # Reads the log into a list, where each list item is a list with the row data.
    with open(log_path, newline="") as log:
        log_read = csv.reader(log)
        log_rows_list = list(log_read)

    # Makes a new version of log_rows_list that has consistent data for comparison to expected values.
    updated_rows_list = []
    for row in log_rows_list:

        # Does not edit the header.
        if row[0] == "Time Started":
            updated_rows_list.append(row)
            continue

        # Remove the time stamp, which is the last 16 characters ( HH:MM:SS.######).
        # The columns are Time Started, Preservation.xml Valid, and Bag Valid.
        row[0] = row[0][:-16]
        row[8] = row[8][:-16]
        row[9] = row[9][:-16]

        # Changes the FITS Tool Errors column back to no errors, if present.
        # FITS does not always have a tool error on the test files.
        if row[5] == "FITS tools generated errors (saved to metadata folder)":
            row[5] = "No FITS tools errors"

        updated_rows_list.append(row)

    return updated_rows_list


class TestFullScript(unittest.TestCase):

    def tearDown(self):
        """
        Deletes the copy of files used for testing, along with the script outputs for the test.
        """
        if os.path.exists("born_digital_current"):
            shutil.rmtree("born_digital_current")
        elif os.path.exists("web_current"):
            shutil.rmtree("web_current")

    def test_born_digital(self):
        """
        Runs the entire script on born-digital test files.
        """
        # Make a copy of the test files stored in the script repo, since the test will alter the files.
        shutil.copytree("born_digital_files", "born_digital_current")

        # Runs the script.
        script_path = os.path.join("..", "general_aip.py")
        aip_dir = os.path.join(os.getcwd(), "born_digital_current", "aip_directory")
        subprocess.run(f'python "{script_path}" "{aip_dir}"', shell=True)

        # Test for the contents of the test_current folder.
        actual = path_list("born_digital_current")
        bag_one = os.path.join("born_digital_current", "aip_directory", "test-001-er-000001_bag")
        bag_two = os.path.join("born_digital_current", "aip_directory", "test-001-er-000002_bag")
        bag_three = os.path.join("born_digital_current", "aip_directory", "test-001-er-000003_bag")
        expected = [os.path.join("born_digital_current", "aips-to-ingest"),
                    os.path.join("born_digital_current", "aip_directory"),
                    os.path.join("born_digital_current", "fits-xml"),
                    os.path.join("born_digital_current", "preservation-xml"),
                    os.path.join("born_digital_current", "aip_log.csv"),
                    os.path.join("born_digital_current", "aips-to-ingest", "manifest_test.txt"),
                    os.path.join("born_digital_current", "aips-to-ingest", "test-001-er-000001_bag.1000.tar.bz2"),
                    os.path.join("born_digital_current", "aips-to-ingest", "test-001-er-000002_bag.1000.tar.bz2"),
                    os.path.join("born_digital_current", "aips-to-ingest", "test-001-er-000003_bag.1000.tar.bz2"),
                    bag_one,
                    bag_two,
                    bag_three,
                    os.path.join("born_digital_current", "aip_directory", "metadata.csv"),
                    os.path.join(bag_one, "data"),
                    os.path.join(bag_one, "bag-info.txt"),
                    os.path.join(bag_one, "bagit.txt"),
                    os.path.join(bag_one, "manifest-md5.txt"),
                    os.path.join(bag_one, "manifest-sha256.txt"),
                    os.path.join(bag_one, "tagmanifest-md5.txt"),
                    os.path.join(bag_one, "tagmanifest-sha256.txt"),
                    os.path.join(bag_one, "data", "metadata"),
                    os.path.join(bag_one, "data", "objects"),
                    os.path.join(bag_one, "data", "metadata", "Flower2.JPG_fits.xml"),
                    os.path.join(bag_one, "data", "metadata", "test-001-er-000001_preservation.xml"),
                    os.path.join(bag_one, "data", "objects", "Flower2.JPG"),
                    os.path.join(bag_two, "data"),
                    os.path.join(bag_two, "bag-info.txt"),
                    os.path.join(bag_two, "bagit.txt"),
                    os.path.join(bag_two, "manifest-md5.txt"),
                    os.path.join(bag_two, "manifest-sha256.txt"),
                    os.path.join(bag_two, "tagmanifest-md5.txt"),
                    os.path.join(bag_two, "tagmanifest-sha256.txt"),
                    os.path.join(bag_two, "data", "metadata"),
                    os.path.join(bag_two, "data", "objects"),
                    os.path.join(bag_two, "data", "metadata", "New Text Document.txt_fits.xml"),
                    os.path.join(bag_two, "data", "metadata", "overview-tree.html_fits.xml"),
                    os.path.join(bag_two, "data", "metadata", "test-001-er-000002_preservation.xml"),
                    os.path.join(bag_two, "data", "objects", "New Text Document.txt"),
                    os.path.join(bag_two, "data", "objects", "overview-tree.html"),
                    os.path.join(bag_three, "data"),
                    os.path.join(bag_three, "bag-info.txt"),
                    os.path.join(bag_three, "bagit.txt"),
                    os.path.join(bag_three, "manifest-md5.txt"),
                    os.path.join(bag_three, "manifest-sha256.txt"),
                    os.path.join(bag_three, "tagmanifest-md5.txt"),
                    os.path.join(bag_three, "tagmanifest-sha256.txt"),
                    os.path.join(bag_three, "data", "metadata"),
                    os.path.join(bag_three, "data", "objects"),
                    os.path.join(bag_three, "data", "metadata", "Test PDF.pdf_fits.xml"),
                    os.path.join(bag_three, "data", "metadata", "test-001-er-000003_preservation.xml"),
                    os.path.join(bag_three, "data", "metadata", "Worksheet.csv_fits.xml"),
                    os.path.join(bag_three, "data", "objects", "Spreadsheet"),
                    os.path.join(bag_three, "data", "objects", "Test PDF.pdf"),
                    os.path.join(bag_three, "data", "objects", "Spreadsheet", "Worksheet.csv"),
                    os.path.join("born_digital_current", "fits-xml", "test-001-er-000001_combined-fits.xml"),
                    os.path.join("born_digital_current", "fits-xml", "test-001-er-000002_combined-fits.xml"),
                    os.path.join("born_digital_current", "fits-xml", "test-001-er-000003_combined-fits.xml"),
                    os.path.join("born_digital_current", "preservation-xml", "test-001-er-000001_preservation.xml"),
                    os.path.join("born_digital_current", "preservation-xml", "test-001-er-000002_preservation.xml"),
                    os.path.join("born_digital_current", "preservation-xml", "test-001-er-000003_preservation.xml")]
        self.assertEqual(actual, expected, "Problem with test for born-digital, folder")

        # Test for the contents of the aip_log.csv file.
        actual_log = log_list(os.path.join("born_digital_current", "aip_log.csv"))
        today = datetime.date.today().strftime("%Y-%m-%d")
        expected_log = [["Time Started", "AIP ID", "Files Deleted", "Objects Folder", "Metadata Folder",
                         "FITS Tool Errors", "FITS Combination Errors", "Preservation.xml Made",
                         "Preservation.xml Valid", "Bag Valid", "Package Errors", "Manifest Errors",
                         "Processing Complete"],
                        [today, "test-001-er-000001", "No files deleted", "Successfully created objects folder",
                         "Successfully created metadata folder", "No FITS tools errors",
                         "Successfully created combined-fits.xml", "Successfully created preservation.xml",
                         f"Preservation.xml valid on {today}", f"Bag valid on {today}", "Successfully made package",
                         "Successfully added AIP to manifest", "Successfully completed processing"],
                        [today, "test-001-er-000002", "No files deleted", "Successfully created objects folder",
                        "Successfully created metadata folder", "No FITS tools errors",
                         "Successfully created combined-fits.xml", "Successfully created preservation.xml",
                         f"Preservation.xml valid on {today}", f"Bag valid on {today}", "Successfully made package",
                         "Successfully added AIP to manifest", "Successfully completed processing"],
                        [today, "test-001-er-000003", "No files deleted", "Successfully created objects folder",
                         "Successfully created metadata folder", "No FITS tools errors",
                         "Successfully created combined-fits.xml", "Successfully created preservation.xml",
                         f"Preservation.xml valid on {today}", f"Bag valid on {today}", "Successfully made package",
                         "Successfully added AIP to manifest", "Successfully completed processing"]]
        self.assertEqual(actual_log, expected_log, "Problem with test for born-digital, log")

    def test_web(self):
        """
        Runs the entire script on web files downloaded from Archive-It.
        """
        # Make a copy of the test files stored in the script repo, since the test will alter the files.
        shutil.copytree("web_files", "web_current")

        # Runs the script.
        script_path = os.path.join(os.path.dirname(os.getcwd()), "general_aip.py")
        aip_dir = os.path.join(os.getcwd(), "web_current", "preservation_download")
        subprocess.run(f'python "{script_path}" "{aip_dir}"', shell=True)

        # Test for the contents of the test_current folder.
        actual = path_list("web_current")
        bag_one = os.path.join("web_current", "preservation_download", "rbrl-377-web-201907-0001_bag")
        warc_one = "ARCHIVEIT-12264-TEST-JOB943446-SEED2027776-20190710131748634-00000-h3.warc"
        bag_two = os.path.join("web_current", "preservation_download", "rbrl-498-web-201907-0001_bag")
        warc_two = "ARCHIVEIT-12265-TEST-JOB943048-SEED2027707-20190709144234143-00000-h3.warc"
        expected = [os.path.join("web_current", "aips-to-ingest"),
                    os.path.join("web_current", "fits-xml"),
                    os.path.join("web_current", "preservation-xml"),
                    os.path.join("web_current", "preservation_download"),
                    os.path.join("web_current", "aip_log.csv"),
                    os.path.join("web_current", "aips-to-ingest", "manifest_russell.txt"),
                    os.path.join("web_current", "aips-to-ingest", "rbrl-377-web-201907-0001_bag.1000.tar.bz2"),
                    os.path.join("web_current", "aips-to-ingest", "rbrl-498-web-201907-0001_bag.1000.tar.bz2"),
                    os.path.join("web_current", "fits-xml", "rbrl-377-web-201907-0001_combined-fits.xml"),
                    os.path.join("web_current", "fits-xml", "rbrl-498-web-201907-0001_combined-fits.xml"),
                    os.path.join("web_current", "preservation-xml", "rbrl-377-web-201907-0001_preservation.xml"),
                    os.path.join("web_current", "preservation-xml", "rbrl-498-web-201907-0001_preservation.xml"),
                    bag_one,
                    bag_two,
                    os.path.join("web_current", "preservation_download", "metadata.csv"),
                    os.path.join(bag_one, "data"),
                    os.path.join(bag_one, "bag-info.txt"),
                    os.path.join(bag_one, "bagit.txt"),
                    os.path.join(bag_one, "manifest-md5.txt"),
                    os.path.join(bag_one, "manifest-sha256.txt"),
                    os.path.join(bag_one, "tagmanifest-md5.txt"),
                    os.path.join(bag_one, "tagmanifest-sha256.txt"),
                    os.path.join(bag_one, "data", "metadata"),
                    os.path.join(bag_one, "data", "objects"),
                    os.path.join(bag_one, "data", "metadata", f"{warc_one}_fits.xml"),
                    os.path.join(bag_one, "data", "metadata", "rbrl-377-web-201907-0001_31104250884_crawldef.csv"),
                    os.path.join(bag_one, "data", "metadata", "rbrl-377-web-201907-0001_943446_crawljob.csv"),
                    os.path.join(bag_one, "data", "metadata", "rbrl-377-web-201907-0001_coll.csv"),
                    os.path.join(bag_one, "data", "metadata", "rbrl-377-web-201907-0001_collscope.csv"),
                    os.path.join(bag_one, "data", "metadata", "rbrl-377-web-201907-0001_preservation.xml"),
                    os.path.join(bag_one, "data", "metadata", "rbrl-377-web-201907-0001_seed.csv"),
                    os.path.join(bag_one, "data", "objects", warc_one),
                    os.path.join(bag_two, "data"),
                    os.path.join(bag_two, "bag-info.txt"),
                    os.path.join(bag_two, "bagit.txt"),
                    os.path.join(bag_two, "manifest-md5.txt"),
                    os.path.join(bag_two, "manifest-sha256.txt"),
                    os.path.join(bag_two, "tagmanifest-md5.txt"),
                    os.path.join(bag_two, "tagmanifest-sha256.txt"),
                    os.path.join(bag_two, "data", "metadata"),
                    os.path.join(bag_two, "data", "objects"),
                    os.path.join(bag_two, "data", "metadata", f"{warc_two}_fits.xml"),
                    os.path.join(bag_two, "data", "metadata", "rbrl-498-web-201907-0001_31104250630_crawldef.csv"),
                    os.path.join(bag_two, "data", "metadata", "rbrl-498-web-201907-0001_943048_crawljob.csv"),
                    os.path.join(bag_two, "data", "metadata", "rbrl-498-web-201907-0001_coll.csv"),
                    os.path.join(bag_two, "data", "metadata", "rbrl-498-web-201907-0001_collscope.csv"),
                    os.path.join(bag_two, "data", "metadata", "rbrl-498-web-201907-0001_preservation.xml"),
                    os.path.join(bag_two, "data", "metadata", "rbrl-498-web-201907-0001_seed.csv"),
                    os.path.join(bag_two, "data", "metadata", "rbrl-498-web-201907-0001_seedscope.csv"),
                    os.path.join(bag_two, "data", "objects", warc_two)]
        self.assertEqual(actual, expected, "Problem with test for web, folder")

        # Test for the contents of the aip_log.csv file.
        actual_log = log_list(os.path.join("web_current", "aip_log.csv"))
        today = datetime.date.today().strftime("%Y-%m-%d")
        expected_log = [["Time Started", "AIP ID", "Files Deleted", "Objects Folder", "Metadata Folder",
                         "FITS Tool Errors", "FITS Combination Errors", "Preservation.xml Made",
                         "Preservation.xml Valid", "Bag Valid", "Package Errors", "Manifest Errors",
                         "Processing Complete"],
                        [today, "rbrl-498-web-201907-0001", "No files deleted", "Successfully created objects folder",
                         "Successfully created metadata folder", "No FITS tools errors",
                         "Successfully created combined-fits.xml", "Successfully created preservation.xml",
                         f"Preservation.xml valid on {today}", f"Bag valid on {today}", "Successfully made package",
                         "Successfully added AIP to manifest", "Successfully completed processing"],
                        [today, "rbrl-377-web-201907-0001", "No files deleted", "Successfully created objects folder",
                        "Successfully created metadata folder", "No FITS tools errors",
                         "Successfully created combined-fits.xml", "Successfully created preservation.xml",
                         f"Preservation.xml valid on {today}", f"Bag valid on {today}", "Successfully made package",
                         "Successfully added AIP to manifest", "Successfully completed processing"]]
        self.assertEqual(actual_log, expected_log, "Problem with test for web, log")


if __name__ == "__main__":
    unittest.main()
