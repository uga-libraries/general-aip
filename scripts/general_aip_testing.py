"""Purpose: Creates AIPs from folders of digital objects but purposefully generates errors.
Used for testing error handling in the script general_aip.py script.

Prior to running the script:
    1. Make one folder per AIP with the digital objects for those AIPs.
    2. All folders to be made into AIPs should be in a single folder (the AIPs directory).
    3. Make a file named metadata.csv in the AIPs directory. See README for what to include.
"""

# Script usage: python '/path/general_aip.py' '/path/aips_directory'

import csv
import datetime
import os
import platform
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import bagit

import aip_functions as a
import configuration as c

# ----------------------------------------------------------------------------------------
# Different versions of AIP functions that produce the required errors for testing.
# ----------------------------------------------------------------------------------------


def extract_metadata_error(aip, error_type):
    """Extracts technical metadata from the files in the objects folder using FITS and creates a single XML file that
    combines the FITS output for every file in the AIP. For testing, produces an error of the requested error type
    before trying to combine the FITS XML into a single file."""

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
            # Edits every fits.xml file to produce the required error.
            # Replaces the file with a blank file.
            if error_type == "empty":
                with open(f'{aip.id}/metadata/{new_name}', "w"):
                    pass
            # Replaces the contents of the file file with a line of text so it is no longer xml.
            elif error_type == "not-xml":
                with open(f'{aip.id}/metadata/{new_name}', "w") as file:
                    file.write("Replacement text.")
            # Replaces one of the XML tags with a different name so it has no closing tag and is not valid xml.
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


def make_preservationxml_error(aip, workflow, error_type):
    """Creates PREMIS and Dublin Core metadata from the combined FITS XML and saves it as a file
    named preservation.xml that meets the metadata requirements for the UGA Libraries' digital
    preservation system (ARCHive). For testing, produces an error of the request type right before the step
    which should catch the error. """

    # Makes a simplified version of the combined fits XML so the XML is easier to aggregate.
    # Saves the file in the AIP's metadata folder. It is deleted at the end of the function.
    combined_fits = f'{aip.id}/metadata/{aip.id}_combined-fits.xml'
    cleanup_stylesheet = f'{c.STYLESHEETS}/fits-cleanup.xsl'
    # Changes the path of the stylesheet to a file that doesn't exist so cleaned_output contains an error.
    if error_type == "cleaned-fits":
        cleanup_stylesheet = f'{c.STYLESHEETS}/error.xsl'
    cleaned_fits = f'{aip.id}/metadata/{aip.id}_cleaned-fits.xml'
    cleaned_output = subprocess.run(
        f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{combined_fits}" -xsl:"{cleanup_stylesheet}" -o:"{cleaned_fits}"',
        stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, moves the AIP to an error folder and does not execute the rest of this function.
    if cleaned_output.stderr:
        aip.log["PresXML"] = f"Issue when creating cleaned-fits.xml. Saxon error: {cleaned_output.stderr.decode('utf-8')}"
        aip.log["Complete"] = "Error during processing."
        a.log(aip.log)
        a.move_error('cleaned_fits_saxon_error', aip.id)
        return

    # Makes the preservation.xml file using a stylesheet and saves it to the AIP's metadata folder.
    stylesheet = f'{c.STYLESHEETS}/fits-to-preservation.xsl'
    # Changes the path of the stylesheet to a file that doesn't exist so pres_output contains an error.
    if error_type == "pres-saxon":
        stylesheet = f'{c.STYLESHEETS}/error.xsl'
    preservation_xml = f'{aip.id}/metadata/{aip.id}_preservation.xml'
    arguments = f'collection-id="{aip.collection_id}" aip-id="{aip.id}" aip-title="{aip.title}" ' \
                f'department="{aip.department}" version={aip.version} workflow="{workflow}" ns={c.NAMESPACE}'
    pres_output = subprocess.run(
        f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{cleaned_fits}" -xsl:"{stylesheet}" -o:"{preservation_xml}" {arguments}',
        stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, moves the AIP to an error folder and does not execute the rest of this function.
    if pres_output.stderr:
        aip.log["PresXML"] = f"Issue when creating preservation.xml. Saxon error: {pres_output.stderr.decode('utf-8')}"
        aip.log["Complete"] = "Error during processing."
        a.log(aip.log)
        a.move_error('pres_xml_saxon_error', aip.id)
        return

    # Deletes the preservation.xml file so the validation step has the failed to load error.
    if error_type == "pres-xmllint":
        os.remove(preservation_xml)

    # Replaces text in the preservation.xml so the validation step has the failed to validate error.
    # Includes all validation error types: empty element, element that doesn't match controlled vocabulary,
    # element that should not repeat, missing element.
    if error_type == "validation":
        with open(f'{aip.id}/metadata/{aip.id}_preservation.xml', "r") as file:
            data = file.read()
            data = data.replace('<dc:title>Test AIP 9</dc:title>', '<dc:title></dc:title>')
            data = data.replace('<premis:objectCategory>file</premis:objectCategory>',
                                '<premis:objectCategory>ERROR</premis:objectCategory>')
            data = data.replace('<premis:size>11</premis:size>',
                                '<premis:size>11</premis:size><premis:size>ERROR</premis:size>')
            data = data.replace('<premis:relatedObjectIdentifierValue>rbrl-000</premis:relatedObjectIdentifierValue>',
                                '')
        with open(f'{aip.id}/metadata/{aip.id}_preservation.xml', "w") as file:
            file.write(data)

    # Validates the preservation.xml file against the requirements of ARCHive.
    # If it is not valid, moves the AIP to an error folder and does not execute the rest of this function.
    validation = subprocess.run(f'xmllint --noout -schema "{c.STYLESHEETS}/preservation.xsd" "{preservation_xml}"',
                                stderr=subprocess.PIPE, shell=True)
    validation_result = validation.stderr.decode('utf-8')

    # This error happens if the preservation.xml file was not made in the expected location.
    # It will probably not happen now that the script tests for saxon errors, but leaving just in case.
    if 'failed to load' in validation_result:
        aip.log["PresXML"] = f"Preservation.xml was not created. xmllint error: {validation_result}"
        aip.log["Complete"] = "Error during processing."
        a.log(aip.log)
        a.move_error('preservationxml_not_found', aip.id)
        return
    else:
        aip.log["PresXML"] = "Successfully created preservation.xml"

    # This error happens if the preservation.xml file does not meet the Libraries' requirements.
    # The validation output is saved to a file in the error folder for review.
    if 'fails to validate' in validation_result:
        aip.log["PresValid"] = "Preservation.xml is not valid (see log in error folder)"
        aip.log["Complete"] = "Error during processing."
        a.log(aip.log)
        a.move_error('preservationxml_not_valid', aip.id)
        with open(f"../errors/preservationxml_not_valid/{aip.id}_presxml_validation.txt", "w") as validation_log:
            for line in validation_result.split("\r"):
                validation_log.write(line + "\n")
        return
    else:
        aip.log["PresValid"] = f"Preservation.xml valid on {datetime.datetime.now()}"

    # Copies the preservation.xml file to the preservation-xml folder for staff reference.
    shutil.copy2(f'{aip.id}/metadata/{aip.id}_preservation.xml', '../preservation-xml')

    # Moves the combined-fits.xml file to the fits-xml folder for staff reference.
    os.replace(f'{aip.id}/metadata/{aip.id}_combined-fits.xml', f'../fits-xml/{aip.id}_combined-fits.xml')

    # Deletes the cleaned-fits.xml file because it is a temporary file.
    os.remove(f'{aip.id}/metadata/{aip.id}_cleaned-fits.xml')


def bag_error(aip, error_type):
    """Bags and validates the AIP. Adds _bag to the AIP folder name.
    For testing, creates an error in the bag (determined by error_type) before validating."""

    # Bags the AIP folder in place with md5 and sha256 checksums for extra security.
    bagit.make_bag(aip.id, checksums=['md5', 'sha256'])

    # Renames the AIP folder to add _bag to the end of the folder name.
    new_aip_name = f'{aip.id}_bag'
    os.replace(aip.id, new_aip_name)

    # Produces the error indicated by error_type.
    if error_type == "file-missing":
        os.remove(f"{aip.id}_bag/data/metadata/{aip.id}_preservation.xml")
    elif error_type == "file-changed":
        with open(f'{aip.id}_bag/data/metadata/{aip.id}_preservation.xml', "r") as file:
            data = file.read()
            data = data.replace('<premis:size>11</premis:size>', '<premis:size>10</premis:size>')
        with open(f'{aip.id}_bag/data/metadata/{aip.id}_preservation.xml', "w") as file:
            file.write(data)
    elif error_type == "manifest-missing":
        os.remove(f"{aip.id}_bag/manifest-sha256.txt")
    elif error_type == "fixity-changed":
        with open(f'{aip.id}_bag/manifest-md5.txt', "r") as file:
            data = file.read()
            data = data.replace('db68a6da2e69c91a11ae4a6b66964f59', 'xxxxxxxxxxxxxxxxxxxxxxxxx')
        with open(f'{aip.id}_bag/manifest-md5.txt', "w") as file:
            file.write(data)

    # Validates the bag.
    # If it is not valid, saves the validation errors to the log, moves the AIP to an error folder.
    new_bag = bagit.Bag(new_aip_name)
    try:
        new_bag.validate()
    except bagit.BagValidationError as errors:
        aip.log["BagValid"] = "Bag not valid (see log in AIP folder)"
        aip.log["Complete"] = "Error during processing."
        a.log(aip.log)
        a.move_error('bag_not_valid', f'{aip.id}_bag')
        with open(f"../errors/bag_not_valid/{aip.id}_bag_validation.txt", "w") as validation_log:
            if errors.details:
                for error_type in errors.details:
                    validation_log.write(str(error_type) + "\n")
            else:
                validation_log.write(str(errors))
        return

    aip.log["BagValid"] = f"Bag valid on {datetime.datetime.now()}"


def package_error(aip):
    """Tars and zips the AIP. Saves the resulting packaged AIP in the aips-to-ingest folder.
    For error testing, there is an error in the 7zip command for making the tar."""

    # Get operating system, since the tar and zip commands are different for Windows and Mac/Linux.
    operating_system = platform.system()

    # Makes a variable for the AIP folder name, which is reused a lot.
    aip_bag = f'{aip.id}_bag'

    # Gets the total size of the bag:
    # sum of the bag payload (data folder) from bag-info.txt and the size of the bag metadata files.
    # It saves time to use the bag payload instead of recalculating the size of a large data folder.
    bag_size = 0
    bag_info = open(f"{aip_bag}/bag-info.txt", "r")
    for line in bag_info:
        if line.startswith("Payload-Oxum"):
            payload = line.split()[1]
            bag_size += float(payload)
    for file in os.listdir(aip_bag):
        if file.endswith('.txt'):
            bag_size += os.path.getsize(f"{aip_bag}/{file}")
    bag_size = int(bag_size)

    # Tars the file, using the command appropriate for the operating system.
    # To make the error, giving the wrong name for the AIP bag to be tarred.
    if operating_system == "Windows":
        # Does not print the progress to the terminal (stdout), which is a lot of text. [subprocess.DEVNULL]
        tar_output = subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -ttar a "{aip_bag}.tar" "{aip.directory}/aip_error_bag"',
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    else:
        subprocess.run(f'tar -cf "{aip_bag}.tar" "{aip_bag}"', shell=True)

    # For Windows, checks for errors from 7z.
    # If there is an error, saves the error to the log and does not complete the rest of the function for this AIP.
    # Cannot move it to an error folder because getting a permissions error.
    if operating_system == "Windows" and not tar_output.stderr == b'':
        aip.log["Package"] = f"Could not tar. 7zip error: {tar_output.stderr.decode('utf-8').strip()}"
        aip.log["Complete"] = "Error during processing."
        a.log(aip.log)
        return

    # Renames the file to include the size.
    os.replace(f'{aip_bag}.tar', f'{aip_bag}.{bag_size}.tar')

    # Updates the size in the AIP object so it can be used by the manifest() function later.
    aip.size = bag_size

    # If the AIP should be zipped (if the value of to_zip is true),
    # Zips (bz2) the tar file, using the command appropriate for the operating system.
    if aip.to_zip is True:
        if operating_system == "Windows":
            # Does not print the progress to the terminal (stdout), which is a lot of text.
            subprocess.run(
                f'"C:/Program Files/7-Zip/7z.exe" -tbzip2 a -aoa "{aip_bag}.{bag_size}.tar.bz2" "{aip_bag}.{bag_size}.tar"',
                stdout=subprocess.DEVNULL, shell=True)
        else:
            subprocess.run(f'bzip2 "{aip_bag}.{bag_size}.tar"', shell=True)

        # Deletes the tar version. Just want the tarred and zipped version.
        # For Mac/Linux, the bzip2 command overwrites the tar file so this step is unnecessary.
        if operating_system == "Windows":
            os.remove(f'{aip_bag}.{bag_size}.tar')

        # Moves the tarred and zipped version to the aips-to-ingest folder.
        path = os.path.join(f'../aips-to-ingest', f"{aip_bag}.{bag_size}.tar.bz2")
        os.replace(f"{aip_bag}.{bag_size}.tar.bz2", path)

    # If not zipping, moves the tarred version to the aips-to-ingest folder.
    else:
        path = os.path.join(f'../aips-to-ingest', f"{aip_bag}.{bag_size}.tar")
        os.replace(f"{aip_bag}.{bag_size}.tar", path)

    # Updates log with success.
    aip.log["Package"] = "Successfully made package"


def manifest_error(aip, error_type):
    """Uses md5deep to calculate the MD5 for the AIP and adds it to the manifest for that department
    in the aips-to-ingest folder. Each department has a separate manifest so AIPs for multiple departments
    may be created simultaneously. For testing, creates an error determined by error_type."""

    # Makes the path to the packaged AIP, which is different depending on if it is zipped or not.
    aip_path = os.path.join(f"../aips-to-ingest", f"{aip.id}_bag.{aip.size}.tar")
    if aip.to_zip is True:
        aip_path = aip_path + ".bz2"

    # For error testing, deletes the AIP from aips-to-ingest.
    if error_type == "missing":
        os.remove(aip_path)

    # Checks if the tar/zip is present in the aips-to-ingest directory.
    # If it isn't, due to errors from package(), does not complete the rest of the function.
    # The error should probably be in the log from package(), but adds it if not.
    if not os.path.exists(aip_path):
        if not aip.log["Package"].startswith("Could not tar."):
            aip.log["Package"] = "Tar/zip file not in aips-to-ingest folder."
            aip.log["Complete"] = "Error during processing."
            a.log(aip.log)
        return

    # For error testing, changes the AIP path.
    if error_type == "md5deep":
        aip_path = "../aips-to-ingest/error_bag.size.tar.bz2"

    # Calculates the MD5 of the packaged AIP.
    md5deep_output = subprocess.run(f'"{c.MD5DEEP}" -br "{aip_path}"',
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # If md5deep has an error, does not execute the rest of this function.
    if md5deep_output.stderr:
        aip.log["Manifest"] = f"Issue when generating MD5. md5deep error: {md5deep_output.stderr.decode('utf-8')}"
        aip.log["Complete"] = "Error during processing."
        a.log(aip.log)
        return

    # Adds the md5 and AIP filename to the department's manifest in the aips-to-ingest folder.
    # Initial output of md5deep is b'md5_value  filename.ext\r\n'
    # Converts to a string and remove the \r linebreak to format the manifest text file as required by ARCHive.
    manifest_path = os.path.join(f"../aips-to-ingest", f"manifest_{aip.department}.txt")
    with open(manifest_path, 'a', encoding='utf-8') as manifest_file:
        manifest_file.write(md5deep_output.stdout.decode("UTF-8").replace("\r", ""))

    # This is the last step, so logs that the AIP completed successfully.
    aip.log["Complete"] = "Successfully completed processing"
    a.log(aip.log)


# ---------------------------------------------------------------------------------------
# THIS PART OF THE SCRIPT IS FOR TESTING SCRIPT INPUTS AND IS IDENTICAL TO general_aip.py,
# EXCEPT FOR WHERE IT MAKES THE TEST FILES.
# THESE STEPS MAKE SURE THERE ARE NO SETUP ERRORS BEFORE BEGINNING THE ERROR TESTS.
# ---------------------------------------------------------------------------------------

# Verifies the script arguments are correct and calculates the associated variables.
# If there are errors, ends the script.
# For testing, continues if aip_metadata_csv not assigned, since script makes that later.
AIPS_DIRECTORY, ZIP, aip_metadata_csv, argument_errors = a.check_arguments(sys.argv)
if len(argument_errors) > 0 and not argument_errors == ["Missing the required file metadata.csv in the AIPs directory."]:
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

# Makes the test files and the manifest.csv file in the AIPs directory.
# Each AIP folder contains a single text file.
for number in range(1, 17):
    folder = f"Folder {number}"
    os.mkdir(folder)
    with open(f"{folder}/file_{number}.txt", "w") as file:
        file.write("Test file.")
    with open("metadata.csv", "a", newline="") as metadata_file:
        metadata_writer = csv.writer(metadata_file)
        if number == 1:
            metadata_writer.writerow(["Department", "Collection", "Folder", "AIP_ID", "Title", "Version"])
        metadata_writer.writerow(["test", "999", folder, f"test-999-er-{format(number, '06d')}", f"Test AIP {number}", 1])

# For testing, makes the metadata_csv variable. In usual script, this is made by check_arguments().
aip_metadata_csv = os.path.join(AIPS_DIRECTORY, "metadata.csv")

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

    # TEST 6: Saxon error while making cleaned-fits.xml.
    if CURRENT_AIP == 6:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there are 4 possible errors to catch.
        if aip.id in os.listdir('.'):
            make_preservationxml_error(aip, 'general', 'cleaned-fits')

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 7: Saxon error while making preservation.xml.
    if CURRENT_AIP == 7:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there are 4 possible errors to catch.
        if aip.id in os.listdir('.'):
            make_preservationxml_error(aip, 'general', 'pres-saxon')

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 8: xmllint error while making preservation.xml.
    if CURRENT_AIP == 8:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there are 4 possible errors to catch.
        if aip.id in os.listdir('.'):
            make_preservationxml_error(aip, 'general', 'pres-xmllint')

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 9: preservation.xml is not valid.
    if CURRENT_AIP == 9:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there are 4 possible errors to catch.
        if aip.id in os.listdir('.'):
            make_preservationxml_error(aip, 'general', 'validation')

        # Remaining workflow steps. Should not run.
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 10: bag is not valid because a file has been deleted.
    if CURRENT_AIP == 10:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there multiple errors to catch.
        if aip.id in os.listdir('.'):
            bag_error(aip, "file-missing")

        # Remaining workflow steps. Should not run.
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 11: bag is not valid because a file has been changed.
    if CURRENT_AIP == 11:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there multiple errors to catch.
        if aip.id in os.listdir('.'):
            bag_error(aip, "file-changed")

        # Remaining workflow steps. Should not run.
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 12: bag is not valid because a manifest is missing.
    if CURRENT_AIP == 12:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there multiple errors to catch.
        if aip.id in os.listdir('.'):
            bag_error(aip, "manifest-missing")

        # Remaining workflow steps. Should not run.
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 13: bag is not valid because fixity for a file has changed.
    if CURRENT_AIP == 13:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')

        # Using a different version of this function which produces the error.
        # It is has an extra parameter for the error to make, since there multiple errors to catch.
        if aip.id in os.listdir('.'):
            bag_error(aip, "fixity-changed")

        # Remaining workflow steps. Should not run.
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 14: tar file is not made.
    if CURRENT_AIP == 14:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)

        # Using a different version of this function which produces the error.
        if f'{aip.id}_bag' in os.listdir('.'):
            package_error(aip)

        # Remaining workflow steps.
        if f'{aip.id}_bag' in os.listdir('.'):
            a.manifest(aip)

    # TEST 15: tar/zip file is not in aips-to-ingest.
    if CURRENT_AIP == 15:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)

        # Using a different version of this function which produces the error.
        if f'{aip.id}_bag' in os.listdir('.'):
            manifest_error(aip, "missing")

    # TEST 16: md5deep gives an error when calculating the MD5.
    if CURRENT_AIP == 16:

        # Start of workflow. Should run correctly.
        if aip.id in os.listdir('.'):
            a.structure_directory(aip)
        if aip.id in os.listdir('.'):
            a.extract_metadata(aip)
        if aip.id in os.listdir('.'):
            a.make_preservationxml(aip, 'general')
        if aip.id in os.listdir('.'):
            a.bag(aip)
        if f'{aip.id}_bag' in os.listdir('.'):
            a.package(aip)

        # Using a different version of this function which produces the error.
        if f'{aip.id}_bag' in os.listdir('.'):
            manifest_error(aip, "md5deep")
