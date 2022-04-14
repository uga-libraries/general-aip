"""Purpose: Creates AIPs from folders of digital objects but purposefully generates errors.
Used for testing error handling in the script general_aip.py script.

Prior to running the script:
    1. Make one folder per AIP with the digital objects for those AIPs.
    2. All folders to be made into AIPs should be in a single folder (the AIPs directory).
    3. Make a file named metadata.csv in the AIPs directory. See README for what to include.
"""

# Script usage: python '/path/general_aip.py' '/path/aips_directory'

import csv
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import aip_functions as a
import configuration as c

# ----------------------------------------------------------------------------------------
# Different versions of AIP functions that produce the required errors for testing.
# ----------------------------------------------------------------------------------------


def extract_metadata_error(aip, error_type):
    """Extracts technical metadata from the files in the objects folder using FITS and creates a single XML file that
    combines the FITS output for every file in the AIP. For testing, produces an error with the FITS files before
    trying to combine them. """

    # Runs FITS on the files in the AIP's objects folder and saves the output to it's metadata folder.
    # The FITS output is named with the original file name. If there is more than one file anywhere
    # within the objects folder with the same name, FITS adds a number to the duplicates, for example:
    # file.ext.fits.xml, file.ext-1.fits.xml, file.ext-2.fits.xml
    fits_output = subprocess.run(
        f'"{c.FITS}" -r -i "{aip.directory}/{aip.id}/objects" -o "{aip.directory}/{aip.id}/metadata"',
        shell=True, stderr=subprocess.PIPE)

    # If there were any tool error messages from FITS, saves those to a log in the AIP's metadata folder.
    # Processing on the AIP continues, since typically other tools still work.
    if fits_output.stderr:
        with open(f"{aip.directory}/{aip.id}/metadata/{aip.id}_fits-tool-errors_fitserr.txt", "w") as fits_errors:
            fits_errors.write(fits_output.stderr.decode('utf-8'))
        aip.log["FITSTool"] = "FITs tools generated errors (saved to metadata folder)"
    else:
        aip.log["FITSTool"] = "No FITS tools errors"

    # Renames the FITS output to the UGA Libraries' metadata naming convention (filename_fits.xml).
    for item in os.listdir(f'{aip.id}/metadata'):
        if item.endswith('.fits.xml'):
            new_name = item.replace('.fits', '_fits')
            os.rename(f'{aip.id}/metadata/{item}', f'{aip.id}/metadata/{new_name}')
            # Edits the FITS output to produce the required error.
            if error_type == "empty":
                with open(f'{aip.id}/metadata/{new_name}', "w"):
                    pass
            elif error_type == "not-xml":
                with open(f'{aip.id}/metadata/{new_name}', "w") as file:
                    file.write("Replacement text.")
            elif error_type == "not-valid":
                with open(f'{aip.id}/metadata/{new_name}', "r") as file:
                    data = file.read()
                    data = data.replace('<identification>', '<id>')
                with open(f'{aip.id}/metadata/{new_name}', "w") as file:
                    file.write(data)

    # The rest of this function copies the FITS output into a single XML file.

    # Makes a new XML object with the root element named combined-fits.
    combo_tree = ET.ElementTree(ET.Element('combined-fits'))
    combo_root = combo_tree.getroot()

    # Gets each of the FITS documents in the AIP's metadata folder.
    for doc in os.listdir(f'{aip.id}/metadata'):
        if doc.endswith('_fits.xml'):

            # Makes Python aware of the FITS namespace.
            ET.register_namespace('', "http://hul.harvard.edu/ois/xml/ns/fits/fits_output")

            # Gets the FITS element and its children and makes it a child of the root, combined-fits.
            try:
                tree = ET.parse(f'{aip.id}/metadata/{doc}')
                root = tree.getroot()
                combo_root.append(root)
            # Errors: the file is empty, is not XML, has invalid XML, or has the wrong namespace.
            # Moves the AIP to an error folder and does not execute the rest of this function.
            except ET.ParseError as error:
                aip.log["FITSError"] = f"Issue when creating combined-fits.xml: {error.msg}"
                aip.log["Complete"] = "Error during processing."
                a.log(aip.log)
                a.move_error('combining_fits', aip.id)
                return

    # Updates the log for any without errors during FITS combination.
    aip.log["FITSError"] = "Successfully created combined-fits.xml"

    # Saves the combined-fits XML to a file named aip-id_combined-fits.xml in the AIP's metadata folder.
    combo_tree.write(f'{aip.id}/metadata/{aip.id}_combined-fits.xml', xml_declaration=True, encoding='UTF-8')


# ---------------------------------------------------------------------------------------
# THIS PART OF THE SCRIPT IS FOR TESTING SCRIPT INPUTS AND IS IDENTICAL TO general_aip.py
# IT MAKES SURE THERE ARE NO SETUP ERRORS BEFORE BEGINNING TO TEST THE DESIRED ERRORS
# ---------------------------------------------------------------------------------------

# Verifies the script arguments are correct and calculates the associated variables.
# If there are errors, ends the script.
AIPS_DIRECTORY, ZIP, aip_metadata_csv, argument_errors = a.check_arguments(sys.argv)
if len(argument_errors) > 0:
    print('The script cannot be run because of the following error(s):')
    for error in argument_errors:
        print("* " + error)
    print('\nScript usage: python "/path/general_aip.py" "/path/aips-directory" [no-zip]')
    sys.exit()

# Makes the current directory the AIPs directory
os.chdir(AIPS_DIRECTORY)

# Verifies all the variables from the configuration file are present and all the paths are valid.
# If not, ends the script.
configuration_errors = a.check_configuration()
if len(configuration_errors) > 0:
    print('\nProblems detected with configuration.py:')
    for error in configuration_errors:
        print(error)
    print('\nCorrect the configuration file and run the script again. Use configuration_template.py as a model.')
    sys.exit()

# Reads the CSV with the AIP metadata.
open_metadata = open(aip_metadata_csv)
read_metadata = csv.reader(open_metadata)

# Verifies the metadata header row has the expected values and matches the folders in the AIPs directory.
# If there is an error, ends the script.
metadata_errors = a.check_metadata_csv(read_metadata)
if len(metadata_errors) > 0:
    print('\nProblems detected with metadata.csv')
    for error in metadata_errors:
        print(error)
    print('\nCorrect the metadata.csv and run the script again.')
    sys.exit()

# If there isn't already a log from running this script on a previous batch,
# starts a log for saving information about events and errors from running the script and adds a header row.
if not os.path.exists('../general_aip_script_log.csv'):
    a.log("header")

# Makes directories used to store script outputs in the same parent folder as the AIPs directory.
a.make_output_directories()

# Starts counts for tracking script progress.
# Some steps are time consuming so this shows the script is not stuck.
# Subtracts one from the count for the metadata file.
CURRENT_AIP = 0
TOTAL_AIPS = len(os.listdir(AIPS_DIRECTORY)) - 1

# Returns to the beginning of the CSV (the script is at the end because of checking it for errors) and skips the header.
open_metadata.seek(0)
next(read_metadata)


# ---------------------------------------------------------------------------------------
# THE REST OF THE SCRIPT CREATES EACH KNOWN ERROR TO TEST IT IS CAUGHT AND LOGGED CORRECTLY.
# ---------------------------------------------------------------------------------------

# Uses the AIP functions to create an AIP for each folder in the metadata CSV.
# Supplies alternative to AIP function when needed to generate an error.
# Even though don't expect the rest of the steps to run after an error, include the code for it just in case.
for aip_row in read_metadata:

    # Makes an instance of the AIP class using metadata from the CSV and global variables.
    department, collection_id, aip_folder, aip_id, title, version = aip_row
    aip = a.AIP(AIPS_DIRECTORY, department, collection_id, aip_folder, aip_id, title, version, ZIP)

    # Updates the current AIP number and displays the script progress in the terminal.
    CURRENT_AIP += 1
    print(f'\n>>>Processing {aip.id} ({CURRENT_AIP} of {TOTAL_AIPS}).')

    # Renames the folder to the AIP ID.
    os.replace(aip.folder_name, aip.id)

    # Deletes any temporary files and makes a log of each deleted file.
    a.delete_temp(aip)

    # TEST 1: an objects folder already exists.
    if CURRENT_AIP == 1:

        # Produce error: add a folder named objects to the aip folder.
        os.mkdir(f"{aip.id}/objects")

        # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure (objects and metadata).
        # Should give an error.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 2: a metadata folder already exists.
    if CURRENT_AIP == 2:

        # Produce error: add a folder named metadata to the aip folder.
        os.mkdir(f"{aip.id}/metadata")

        # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure (objects and metadata).
        # Should give an error.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 3: a FITS file is empty.
    if CURRENT_AIP == 3:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there are 4 possible errors to catch.
        if aip.id in os.listdir('.'):
            extract_metadata_error(aip, "empty")

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 4: a FITS file is not XML.
    if CURRENT_AIP == 4:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there are 4 possible errors to catch.
        if aip.id in os.listdir('.'):
            extract_metadata_error(aip, "not-xml")

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 5: a FITS file is not valid XML.
    if CURRENT_AIP == 5:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there are 4 possible errors to catch.
        if aip.id in os.listdir('.'):
            extract_metadata_error(aip, "not-valid")

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)