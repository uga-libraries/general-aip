""" Functions used to make AIPs from folders of digital objects that are ready for ingest into the
UGA Libraries' digital preservation system (ARCHive). These are utilized by multiple scripts that
create AIPs of different types."""

import csv
import datetime
import os
import platform
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
import bagit

# Constants with the absolute file paths for programs and files used by the functions.
import configuration as c


class AIP:
    def __init__(self, directory, department, collection_id, folder_name, aip_id, title, version, to_zip):
        self.directory = directory
        self.department = department
        self.collection_id = collection_id
        self.folder_name = folder_name
        self.id = aip_id
        self.title = title
        self.version = version
        self.to_zip = to_zip
        self.size = None
        self.log = {"Started": datetime.datetime.now(), "AIP": self.id, "Deletions": "n/a",
                    "ObjectsError": "n/a", "MetadataError": "n/a", "FITSTool": "n/a", "FITSError": "n/a",
                    "PresXML": "n/a", "PresValid": "n/a", "BagValid": "n/a", "Package": "n/a", "Manifest": "n/a",
                    "Complete": "n/a"}


def log(log_data):
    """Saves information about each step done on an AIP to a CSV file.
    Information is stored in a dictionary after each step and saved to the log
    after each AIP either finishes processing or encounters an error."""

    # Formats the data for this row in the log CSV as a list.
    # For the header, uses default values.
    if log_data == "header":
        log_row = ["Time Started", "AIP ID", "Files Deleted", "Objects Folder",
                   "Metadata Folder", "FITS Tool Errors", "FITS Combination Errors", "Preservation.xml Made",
                   "Preservation.xml Valid", "Bag Valid", "Package Errors", "Manifest Errors", "Processing Complete"]

    # In all other cases, log_data is a dictionary, with one key per column in the log.
    # Gets the value of each key in the desired order and adds to a list for saving to the log.
    else:
        log_row = [log_data["Started"], log_data["AIP"], log_data["Deletions"],
                   log_data["ObjectsError"], log_data["MetadataError"], log_data["FITSTool"], log_data["FITSError"],
                   log_data["PresXML"], log_data["PresValid"], log_data["BagValid"], log_data["Package"],
                   log_data["Manifest"], log_data["Complete"]]

    # Saves the data for the row to the log CSV.
    with open('../aip_log.csv', 'a', newline='') as log_file:
        log_writer = csv.writer(log_file)
        log_writer.writerow(log_row)


def move_error(error_name, item):
    """Moves the AIP folder to an error folder, named with the error type, so the rest of the
    workflow steps are not completed on it. Makes the error folder if it does not already exist
    prior to moving the AIP folder. """

    if not os.path.exists(f'../errors/{error_name}'):
        os.makedirs(f'../errors/{error_name}')
    os.replace(item, f'../errors/{error_name}/{item}')


def check_arguments(arguments):
    """Verifies that all the arguments received are correct and calculates variables.
    Returns the variables and a list of errors, if any."""

    # Starts a list for all encountered errors, so all errors can be checked before returning a result.
    errors = []

    # Checks if arguments were given, besides the default of script name. If not, saves an error.
    if len(arguments) == 1:
        aips_directory = None
        errors.append('AIPs directory argument is missing.')

    # Assigns the required script argument to the aips_directory variable, if it is a valid directory.
    # If not, saves an error.
    if len(arguments) > 1:
        if os.path.exists(arguments[1]):
            aips_directory = arguments[1]
        else:
            aips_directory = None
            errors.append('AIPs directory argument is not a valid directory.')

    # If the optional script argument no-zip is present, assigns the zip variable to False. Otherwise, zip is True.
    # no-zip is for AIPs that are larger when zipped and should only be tarred to save space and time.
    if len(arguments) == 3:
        if arguments[2] == "no-zip":
            to_zip = False
        else:
            to_zip = None
            errors.append('Unexpected value for the second argument. If provided, should be "no-zip".')
    else:
        to_zip = True

    # Generates the path to the required metadata file and verifies it is present.
    # Only tests if there is a value for aips_directory, which is part of the path.
    if aips_directory:
        aip_metadata_csv = os.path.join(aips_directory, "metadata.csv")
        if not os.path.exists(aip_metadata_csv):
            errors.append('Missing the required file metadata.csv in the AIPs directory.')
    else:
        aip_metadata_csv = None
        errors.append('Cannot check for the metadata.csv in the AIPs directory because the AIPs directory has an error.')

    # Return the variables and errors list
    return aips_directory, to_zip, aip_metadata_csv, errors


def check_configuration():
    """Verifies all the expected variables are in the configuration file and paths are valid if they are a path.
    Returns a list of paths with errors or "no errors".
    This avoids wasting processing time by doing earlier steps before the path error is encountered."""

    errors = []

    # For the 4 variables with a value that is a path, check if the variable exists.
    # If so check if the path is valid.
    # Either error (doesn't exist or not valid) is added to the errors list.

    try:
        if not os.path.exists(c.FITS):
            errors.append(f"FITS path '{c.FITS}' is not correct.")
    except AttributeError:
        errors.append("FITS variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.SAXON):
            errors.append(f"SAXON path '{c.SAXON}' is not correct.")
    except AttributeError:
        errors.append("SAXON variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.MD5DEEP):
            errors.append(f"MD5DEEP path '{c.MD5DEEP}' is not correct.")
    except AttributeError:
        errors.append("MD5DEEP variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.STYLESHEETS):
            errors.append(f"STYLESHEETS path '{c.STYLESHEETS}' is not correct.")
    except AttributeError:
        errors.append("STYLESHEETS variable is missing from the configuration file.")

    # For the 2 variables where the value is not a path, check if the variable exists.
    # If not, add to the error list.
    try:
        c.NAMESPACE
    except AttributeError:
        errors.append("NAMESPACE variable is missing from the configuration file.")

    try:
        c.GROUPS
    except AttributeError:
        errors.append("GROUPS variable is missing from the configuration file.")

    # Returns the errors list. If there were no errors, it will be empty.
    return errors


def check_metadata_csv(read_metadata):
    """Verifies that the columns are in the required order. If so, verifies that the departments match ARCHive group
    codes and that the AIP list in the CSV matches the folders in the AIPs directory.

    Returns a list of errors or an empty list if there are no errors. """

    # Starts a list for all encountered errors, so all errors can be checked before returning a result.
    errors = []

    # Does a case insensitive comparison of the CSV header row with the required values.
    # If the header is not correct, returns the error and does not test the column values.
    header = next(read_metadata)
    header_lowercase = [name.lower() for name in header]
    if header_lowercase != ['department', 'collection', 'folder', 'aip_id', 'title', 'version']:
        errors.append("The columns in the metadata.csv do not match the required values or order.")
        errors.append("Required: Department, Collection, Folder, AIP_ID, Title, Version")
        errors.append(f"Current:  {', '.join(header)}")
        errors.append("Since the columns are not correct, did not check the column values.")
        return errors

    # Makes a list of all values in the department and folder columns to use for testing.
    csv_dept_list = []
    csv_folder_list = []
    for row in read_metadata:
        csv_dept_list.append(row[0])
        csv_folder_list.append(row[2])

    # Tests the values in the department column.
    # Makes a list of unique values in the column, checks it against the ARCHive groups in the configuration file,
    # and saves any that don't match to the errors list.
    unique_departments = list(set(csv_dept_list))
    unique_departments.sort()
    for department in unique_departments:
        if department not in c.GROUPS:
            errors.append(f"{department} is not an ARCHive group.")

    # The rest of the function tests the folder names.

    # Makes a list of every folder name in the AIPs directory.
    aips_directory_list = []
    for item in os.listdir('.'):
        if os.path.isdir(item):
            aips_directory_list.append(item)

    # Finds any folder names that are in the CSV more than once and adds them to the error list.
    duplicates = [folder for folder in csv_folder_list if csv_folder_list.count(folder) > 1]
    if len(duplicates) > 0:
        unique_duplicates = list(set(duplicates))
        unique_duplicates.sort()
        for duplicate in unique_duplicates:
            errors.append(f"{duplicate} is in the metadata.csv folder column more than once.")

    # Finds any AIPs that are only in the CSV and adds them to the error list.
    just_csv = list(set(csv_folder_list) - set(aips_directory_list))
    if len(just_csv) > 0:
        just_csv.sort()
        for aip in just_csv:
            errors.append(f"{aip} is in metadata.csv and missing from the AIPs directory.")

    # Finds any AIPs that are only in the AIPs directory and adds them to the error list.
    just_aip_dir = list(set(aips_directory_list) - set(csv_folder_list))
    if len(just_aip_dir) > 0:
        just_aip_dir.sort()
        for aip in just_aip_dir:
            errors.append(f"{aip} is in the AIPs directory and missing from metadata.csv.")

    # Returns the errors list. If there were no errors, it will be empty.
    return errors


def make_output_directories():
    """Makes the directories used to store script outputs, if they don't already exist,
    in the parent folder of the AIPs directory."""

    directories = ['aips-to-ingest', 'fits-xml', 'preservation-xml']

    for directory in directories:
        if not os.path.exists(f'../{directory}'):
            os.mkdir(f'../{directory}')


def delete_temp(aip):
    """Deletes temporary files of various types from anywhere within the AIP folder because they cause errors later
    in the workflow, especially with bag validation. Creates a log of the deleted files as a record of actions taken
    on the AIP during processing. This is especially important if there are large files that result in a noticeable
    change in size after making the AIP. """

    # List of files to be deleted where the filename can be matched in its entirely.
    delete = ['.DS_Store', '._.DS_Store', 'Thumbs.db']

    # List of files that were deleted, to save to a log if desired.
    deleted_files = []

    # Checks all files at any level in the AIP folder against deletion criteria.
    # Gets information for the deletion log and then deletes the file.
    for root, directories, files in os.walk(aip.id):
        for item in files:
            if item in delete or item.endswith('.tmp') or item.startswith('.'):
                path = os.path.join(root, item)
                date = time.gmtime(os.path.getmtime(path))
                date_reformatted = f"{date.tm_year}-{date.tm_mon}-{date.tm_mday} {date.tm_hour}:{date.tm_hour}:{date.tm_min}"
                deleted_files.append([path, item, os.path.getsize(path), date_reformatted])
                os.remove(os.path.join(root, item))

    # Creates the log in the AIP folder if any files were deleted.
    # The log contains the path, filename, size in bytes and date/time last modified of every deleted file.
    # Adds event information for deletion to the script log.
    if len(deleted_files) > 0:
        filename = f"{aip.id}_files-deleted_{datetime.datetime.today().date()}_del.csv"
        with open(f"{aip.id}/{filename}", "w", newline="") as deleted_log:
            deleted_log_writer = csv.writer(deleted_log)
            deleted_log_writer.writerow(["Path", "File Name", "Size (Bytes)", "Date Last Modified"])
            for file_data in deleted_files:
                deleted_log_writer.writerow(file_data)
        aip.log["Deletions"] = "File(s) deleted"
    else:
        aip.log["Deletions"] = "No files deleted"


def structure_directory(aip):
    """Makes the AIP directory structure (objects and metadata folders within the AIP folder)
    and moves the digital objects into those folders. Anything not recognized as metadata is
    moved into the objects folder. If the digital objects are organized into folders, that
    directory structure is maintained within the objects folder. """

    # Makes the objects and metadata folders within the AIP folder, if they don't exist.
    # Otherwise, moves the AIP to an error folder so the directory structure is not altered.
    try:
        os.mkdir(f'{aip.id}/objects')
    except FileExistsError:
        aip.log["ObjectsError"] = "Objects folder already exists in original files"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
        move_error("objects_folder_exists", aip.id)
        return
    try:
        os.mkdir(f"{aip.id}/metadata")
    except FileExistsError:
        aip.log["MetadataError"] = "Metadata folder already exists in original files"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
        move_error("metadata_folder_exists", aip.id)
        return

    # Update log that no errors were found for objects or metadata folders.
    aip.log["ObjectsError"] = "Successfully created objects folder"
    aip.log["MetadataError"] = "Successfully created metadata folder"

    # Moves any metadata files, identified by their file names and department if not all use it, to the metadata folder.
    for item in os.listdir(aip.id):
        if item.startswith(f"{aip.id}_files-deleted_"):
            os.replace(f"{aip.id}/{item}", f"{aip.id}/metadata/{item}")
        if aip.department == "emory" and item.startswith("EmoryMD"):
            os.replace(f"{aip.id}/{item}", f"{aip.id}/metadata/{item}")

    # Moves all remaining files and folders to the objects folder.
    # The first level within the AIPs folder is now just the metadata folder and objects folder.
    for item in os.listdir(aip.id):
        if item in ("metadata", "objects"):
            continue
        os.replace(f"{aip.id}/{item}", f"{aip.id}/objects/{item}")


def extract_metadata(aip):
    """Extracts technical metadata from the files in the objects folder using FITS and
    creates a single XML file that combines the FITS output for every file in the AIP. """

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
            # Errors: the file is empty, is not XML, or has invalid XML.
            # Moves the AIP to an error folder and does not execute the rest of this function.
            except ET.ParseError as error:
                aip.log["FITSError"] = f"Issue when creating combined-fits.xml: {error.msg}"
                aip.log["Complete"] = "Error during processing."
                log(aip.log)
                move_error('combining_fits', aip.id)
                return

    # Updates the log for any without errors during FITS combination.
    aip.log["FITSError"] = "Successfully created combined-fits.xml"

    # Saves the combined-fits XML to a file named aip-id_combined-fits.xml in the AIP's metadata folder.
    combo_tree.write(f'{aip.id}/metadata/{aip.id}_combined-fits.xml', xml_declaration=True, encoding='UTF-8')


def make_preservationxml(aip):
    """Creates PREMIS and Dublin Core metadata from the combined FITS XML and saves it as a file
    named preservation.xml that meets the metadata requirements for the UGA Libraries' digital
    preservation system (ARCHive)."""

    # Makes a simplified version of the combined fits XML so the XML is easier to aggregate.
    # Saves the file in the AIP's metadata folder. It is deleted at the end of the function.
    combined_fits = f'{aip.id}/metadata/{aip.id}_combined-fits.xml'
    cleanup_stylesheet = f'{c.STYLESHEETS}/fits-cleanup.xsl'
    cleaned_fits = f'{aip.id}/metadata/{aip.id}_cleaned-fits.xml'
    cleaned_output = subprocess.run(
        f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{combined_fits}" -xsl:"{cleanup_stylesheet}" -o:"{cleaned_fits}"',
        stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, moves the AIP to an error folder and does not execute the rest of this function.
    if cleaned_output.stderr:
        aip.log["PresXML"] = f"Issue when creating cleaned-fits.xml. Saxon error: {cleaned_output.stderr.decode('utf-8')}"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
        move_error('cleaned_fits_saxon_error', aip.id)
        return

    # Makes the preservation.xml file using a stylesheet and saves it to the AIP's metadata folder.
    stylesheet = f'{c.STYLESHEETS}/fits-to-preservation.xsl'
    preservation_xml = f'{aip.id}/metadata/{aip.id}_preservation.xml'
    arguments = f'collection-id="{aip.collection_id}" aip-id="{aip.id}" aip-title="{aip.title}" ' \
                f'department="{aip.department}" version={aip.version} ns={c.NAMESPACE}'
    pres_output = subprocess.run(
        f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{cleaned_fits}" -xsl:"{stylesheet}" -o:"{preservation_xml}" {arguments}',
        stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, moves the AIP to an error folder and does not execute the rest of this function.
    if pres_output.stderr:
        aip.log["PresXML"] = f"Issue when creating preservation.xml. Saxon error: {pres_output.stderr.decode('utf-8')}"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
        move_error('pres_xml_saxon_error', aip.id)
        return

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
        log(aip.log)
        move_error('preservationxml_not_found', aip.id)
        return
    else:
        aip.log["PresXML"] = "Successfully created preservation.xml"

    # This error happens if the preservation.xml file does not meet the Libraries' requirements.
    # The validation output is saved to a file in the error folder for review.
    if 'fails to validate' in validation_result:
        aip.log["PresValid"] = "Preservation.xml is not valid (see log in error folder)"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
        move_error('preservationxml_not_valid', aip.id)
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


def bag(aip):
    """Bags and validates the AIP. Adds _bag to the AIP folder name."""

    # Bags the AIP folder in place with md5 and sha256 checksums for extra security.
    bagit.make_bag(aip.id, checksums=['md5', 'sha256'])

    # Renames the AIP folder to add _bag to the end of the folder name.
    new_aip_name = f'{aip.id}_bag'
    os.replace(aip.id, new_aip_name)

    # Validates the bag.
    # If it is not valid, saves the validation errors to the log, moves the AIP to an error folder.
    new_bag = bagit.Bag(new_aip_name)
    try:
        new_bag.validate()
    except bagit.BagValidationError as errors:
        aip.log["BagValid"] = "Bag not valid (see log in AIP folder)"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
        move_error('bag_not_valid', f'{aip.id}_bag')
        with open(f"../errors/bag_not_valid/{aip.id}_bag_validation.txt", "w") as validation_log:
            if errors.details:
                for error_type in errors.details:
                    validation_log.write(str(error_type) + "\n")
            else:
                validation_log.write(str(errors))
        return

    aip.log["BagValid"] = f"Bag valid on {datetime.datetime.now()}"


def package(aip):
    """Tars and zips the AIP. Saves the resulting packaged AIP in the aips-to-ingest folder.
    Also uses md5 deep to calculate the MD5 for the AIP and adds it to the manifest for that department
    in the aips-to-ingest folder. Each department has a separate manifest so AIPs for multiple departments
    may be created simultaneously."""

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
    if operating_system == "Windows":
        # Does not print the progress to the terminal (stdout), which is a lot of text. [subprocess.DEVNULL]
        tar_output = subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -ttar a "{aip_bag}.tar" "{aip.directory}/{aip_bag}"',
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
    else:
        subprocess.run(f'tar -cf "{aip_bag}.tar" "{aip_bag}"', shell=True)

    # For Windows, checks for errors from 7z.
    # If there is an error, saves the error to the log and does not complete the rest of the function for this AIP.
    # Cannot move it to an error folder because getting a permissions error.
    if operating_system == "Windows" and not tar_output.stderr == b'':
        aip.log["Package"] = f"Could not tar. 7zip error: {tar_output.stderr.decode('utf-8')}"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
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


def manifest(aip):
    """Uses md5deep to calculate the MD5 for the AIP and adds it to the manifest for that department
    in the aips-to-ingest folder. Each department has a separate manifest so AIPs for multiple departments
    may be created simultaneously."""

    # Makes the path to the packaged AIP, which is different depending on if it is zipped or not.
    aip_path = os.path.join(f"../aips-to-ingest", f"{aip.id}_bag.{aip.size}.tar")
    if aip.to_zip is True:
        aip_path = aip_path + ".bz2"

    # Checks if the tar/zip is present in the aips-to-ingest directory.
    # If it isn't, due to errors from package(), does not complete the rest of the function.
    # The error should probably be in the log from package(), but adds it if not.
    if not os.path.exists(aip_path):
        if not aip.log["Package"].startswith("Could not tar."):
            aip.log["Package"] = "Tar/zip file not in aips-to-ingest folder."
            aip.log["Complete"] = "Error during processing."
            log(aip.log)
        return

    # Calculates the MD5 of the packaged AIP.
    md5deep_output = subprocess.run(f'"{c.MD5DEEP}" -br "{aip_path}"',
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # If md5deep has an error, does not execute the rest of this function.
    if md5deep_output.stderr:
        aip.log["Manifest"] = f"Issue when generating MD5. md5deep error: {md5deep_output.stderr.decode('utf-8')}"
        aip.log["Complete"] = "Error during processing."
        log(aip.log)
        return

    # Adds the md5 and AIP filename to the department's manifest in the aips-to-ingest folder.
    # Initial output of md5deep is b'md5_value  filename.ext\r\n'
    # Converts to a string and remove the \r linebreak to format the manifest text file as required by ARCHive.
    manifest_path = os.path.join(f"../aips-to-ingest", f"manifest_{aip.department}.txt")
    with open(manifest_path, 'a', encoding='utf-8') as manifest_file:
        manifest_file.write(md5deep_output.stdout.decode("UTF-8").replace("\r", ""))

    # Logs the success of adding to the manifest.
    aip.log["Manifest"] = "Successfully added AIP to manifest."
    
    # This is the last step, so logs that the AIP completed successfully.
    aip.log["Complete"] = "Successfully completed processing"
    log(aip.log)
