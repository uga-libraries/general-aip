"""
Testing for the entire script, with input that represents the different workflows that use the script.
It does not currently include tests for error handling.
"""

import datetime
import os
import pandas as pd
import re
import shutil
import subprocess
import unittest


def make_aip_log_list(log_path):
    """Reads the aip log and returns a list of lists, where each list is a row in the log,
    with normalization for inconsistent data."""
    df = pd.read_csv(log_path, dtype=str)

    # Remove time stamps, which are the last 16 characters, and leaves just the day to allow comparison,
    # as long as the column is from a correct validation (may also be blank or a validation error).
    df['Time Started'] = df['Time Started'].str[:-16]
    df.loc[df['Preservation.xml Valid'].str.startswith('Preservation.xml valid on', na=False), 'Preservation.xml Valid'] = df['Preservation.xml Valid'].str[:-16]
    df.loc[df['Bag Valid'].str.startswith('Bag valid on', na=False), 'Bag Valid'] = df['Bag Valid'].str[:-16]

    # Make FITS tool error value consistent, since the same files don't always generate an error.
    df.loc[df['FITS Tool Errors'] == 'FITS tools generated errors (saved to metadata folder)', 'FITS Tool Errors'] = 'No FITS tools errors'

    # Normalize direction of slash from xmllint to match other text.
    df['Preservation.xml Made'] = df['Preservation.xml Made'].str.replace('/', '\\')

    # Convert the dataframe to a list of rows.
    df = df.fillna('BLANK')
    make_aip_log_list = [df.columns.to_list()] + df.values.tolist()
    return make_aip_log_list


def make_deletion_make_aip_log_list(log_path):
    """Reads the deletion log and returns a list of lists, where each list is a row in the log
    The time in the Date Last Modified is removed, leaving just the date, so it is predictable for comparison."""
    df = pd.read_csv(log_path)
    df['Date Last Modified'] = df['Date Last Modified'].str.split(' ').str[0]
    df.fillna('BLANK')
    make_aip_log_list = [df.columns.to_list()] + df.values.tolist()
    return make_aip_log_list


def make_directory_list(dir_path):
    """Make a list of the paths of every file and folder in a directory,
    with sorting and normalization for inconsistent data."""
    directory_list = []
    for root, dirs, files in os.walk(dir_path):
        for directory in dirs:
            directory_list.append(os.path.join(root, directory))
        for file in files:
            # The size in the zipped AIP filenames varies each time.
            if root.endswith("aips-ready-to-ingest") and file.endswith(".tar.bz2"):
                file = re.sub(r"_bag.\d+.", "_bag.1000.", file)
            # Skips the FITS tool error log because it is not consistently made and the placeholder files for GitHub.
            if file.endswith("_fits-tool-errors_fitserr.txt") or file == 'Explanation.txt' or file.lower() == 'placeholder.txt':
                continue
            directory_list.append(os.path.join(root, file))
    directory_list.sort(key=str.lower)
    return directory_list


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
        Runs the entire script on born-digital test files. Original folders are not named with the AIP ID.
        """
        # Make a copy of the test files stored in the script repo, since the test will alter the files.
        shutil.copytree("born_digital_files", "born_digital_current")

        # Runs the script.
        script_path = os.path.join("..", "general_aip.py")
        aip_dir = os.path.join(os.getcwd(), "born_digital_current", "aip_directory")
        subprocess.run(f'python "{script_path}" "{aip_dir}"', shell=True)

        # Test for the contents of the test_current folder.
        actual = make_directory_list("born_digital_current")
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
                    os.path.join(bag_one, "data", "objects", "CD001_Images"),
                    os.path.join(bag_one, "data", "objects", "CD001_Images", "Flower2.JPG"),
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
                    os.path.join(bag_two, "data", "objects", "CD002_Random"),
                    os.path.join(bag_two, "data", "objects", "CD002_Random", "New Text Document.txt"),
                    os.path.join(bag_two, "data", "objects", "CD002_Random", "overview-tree.html"),
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
                    os.path.join(bag_three, "data", "objects", "FD001_Text"),
                    os.path.join(bag_three, "data", "objects", "FD001_Text", "Spreadsheet"),
                    os.path.join(bag_three, "data", "objects", "FD001_Text", "Test PDF.pdf"),
                    os.path.join(bag_three, "data", "objects", "FD001_Text", "Spreadsheet", "Worksheet.csv"),
                    os.path.join("born_digital_current", "fits-xml", "test-001-er-000001_combined-fits.xml"),
                    os.path.join("born_digital_current", "fits-xml", "test-001-er-000002_combined-fits.xml"),
                    os.path.join("born_digital_current", "fits-xml", "test-001-er-000003_combined-fits.xml"),
                    os.path.join("born_digital_current", "preservation-xml", "test-001-er-000001_preservation.xml"),
                    os.path.join("born_digital_current", "preservation-xml", "test-001-er-000002_preservation.xml"),
                    os.path.join("born_digital_current", "preservation-xml", "test-001-er-000003_preservation.xml")]
        self.assertEqual(actual, expected, "Problem with test for born-digital, folder")

        # Test for the contents of the aip_log.csv file.
        actual_log = make_aip_log_list(os.path.join("born_digital_current", "aip_log.csv"))
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
        actual = make_directory_list("web_current")
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
        actual_log = make_aip_log_list(os.path.join("web_current", "aip_log.csv"))
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
