"""Functions used to make AIPs from folders of digital objects"""

import csv
from datetime import datetime
import os
import pathlib
import platform
import shutil
import subprocess
import time
import xml.etree.ElementTree as et
import bagit
import configuration as c


class AIP:
    """Characteristics of each AIP and log data used by multiple functions"""

    def __init__(self, directory, department, workflow, collection_id, folder_name, aip_type, aip_id, title, version,
                 to_zip):
        self.directory = directory
        self.department = department
        self.workflow = workflow
        self.collection_id = collection_id
        self.folder_name = folder_name
        self.type = aip_type
        self.id = aip_id
        self.title = title
        self.version = version
        self.to_zip = to_zip
        self.size = None
        self.log = {"Started": datetime.now(), "AIP": self.id, "Deletions": "n/a",
                    "ObjectsError": "n/a", "MetadataError": "n/a", "FITSTool": "n/a", "FITSError": "n/a",
                    "PresXML": "n/a", "PresValid": "n/a", "BagValid": "n/a", "Package": "n/a", "Manifest": "n/a",
                    "Complete": "n/a"}


def check_arguments(arguments):
    """Verify the script arguments are correct and calculate the path to metadata.csv

    Parameters:
        arguments : sys.argv list of script arguments

    Returns:
        aips_directory : the path to the folder which contains the folders to be made into AIPs
        aip_type : the type of AIP, which influences a few steps
        workflow : for AV type, the type of AV workflow, which influences a few steps
        to_zip : a boolean for if the AIPs should be zipped as well as tarred (True) or only tarred (False)
        aip_metadata_csv : the path to the metadata.csv file in the aips_directory
        errors_list : a list of errors, or an empty list if there were no errors
    """

    # Starts a list for all encountered errors, so all errors can be checked before returning a result,
    # and the two variables assigned from arguments are set to None.
    # These are updated to the correct value from the arguments, if they are provided.
    errors_list = []
    aips_directory = None
    aip_type = None
    workflow = None
    to_zip = None

    # Checks if arguments were given, besides the default of script name.
    if len(arguments) == 1:
        errors_list.append('Required arguments are missing: aips_directory, aip_type, and to_zip.')

    # Checks if the first required argument (aips_directory) is present and a valid path.
    if len(arguments) > 1:
        if os.path.exists(arguments[1]):
            aips_directory = arguments[1]
        else:
            errors_list.append(f'Provided aips_directory "{arguments[1]}" is not a valid directory.')

    # Checks if the second required argument (aip_type) is present and an expected value.
    if len(arguments) > 2:
        if arguments[2] in ('av', 'general', 'web'):
            aip_type = arguments[2]
        else:
            errors_list.append(f'Provided aip_type "{arguments[2]}" is not an expected value (av, general, web).')

    # Checks if the third required argument (to_zip) is present, and if so, if it is the expected value.
    if len(arguments) > 3:
        if arguments[3] == "no-zip":
            to_zip = False
        elif arguments[3] == "zip":
            to_zip = True
        else:
            errors_list.append(f'Provided to_zip "{arguments[3]}" is not an expected value (no-zip, zip).')

    # Checks if the optional argument (workflow) is present, and if so, if it is the expected value.
    if len(arguments) > 4:
        if arguments[4] in ('dpx', 'mkv', 'mkv-filmscan', 'mov', 'mp4', 'mxf', 'wav'):
            workflow = arguments[4]
        else:
            errors_list.append(f'Provided workflow "{arguments[4]}" is not an expected value '
                               f'(dpx, mkv, mkv-filmscan, mov, mp4, mxf, wav)')

    # Checks if there are too many arguments.
    if len(arguments) > 5:
        errors_list.append("Too many script arguments. The maximum expected is 4.")

    # Calculates the path to the required metadata file and verifies it is present.
    # Only tests if there is a value for aips_directory, which is part of the path.
    if aips_directory:
        aip_metadata_csv = os.path.join(aips_directory, "metadata.csv")
        if not os.path.exists(aip_metadata_csv):
            aip_metadata_csv = None
            errors_list.append("Missing the required file metadata.csv in the AIPs directory.")
    else:
        aip_metadata_csv = None
        errors_list.append("Cannot check for the metadata.csv because the AIPs directory has an error.")

    # The errors list is empty if there were no errors.
    return aips_directory, aip_type, to_zip, workflow, aip_metadata_csv, errors_list


def check_configuration(aips_dir):
    """Verify the variables in the configuration file are correct

    - All variables are present
    - Path variables are a valid path
    - FITS path starts with the same letter as the aips_directory

    Parameters:
        aips_dir : the path to the folder which contains the folders to be made into AIPs

    Returns:
        errors_list : a list of errors, or an empty list if there were no errors
    """

    # Starts a list for all encountered errors, so all errors can be checked before returning a result.
    errors_list = []

    # For the variables with a value that is a path, checks if the variable exists and if the path is valid.
    try:
        if not os.path.exists(c.AIP_STAGING):
            errors_list.append(f"AIP_STAGING path '{c.AIP_STAGING}' is not correct.")
    except AttributeError:
        errors_list.append("AIP_STAGING variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.INGEST_SERVER):
            errors_list.append(f"INGEST_SERVER path '{c.INGEST_SERVER}' is not correct.")
    except AttributeError:
        errors_list.append("INGEST_SERVER variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.FITS):
            errors_list.append(f"FITS path '{c.FITS}' is not correct.")
        # For FITS, checks that the directory (first character) of the path matches the directory of aips_dir.
        if not c.FITS[0] == aips_dir[0]:
            errors_list.append(f"FITS is not in the same directory as the aips_directory '{aips_dir}'.")
    except AttributeError:
        errors_list.append("FITS variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.SAXON):
            errors_list.append(f"SAXON path '{c.SAXON}' is not correct.")
    except AttributeError:
        errors_list.append("SAXON variable is missing from the configuration file.")

    # MD5DEEP is a path in Windows but just "md5deep" in Mac.
    if not c.MD5DEEP == 'md5deep':
        try:
            if not os.path.exists(c.MD5DEEP):
                errors_list.append(f"MD5DEEP path '{c.MD5DEEP}' is not correct.")
        except AttributeError:
            errors_list.append("MD5DEEP variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.STYLESHEETS):
            errors_list.append(f"STYLESHEETS path '{c.STYLESHEETS}' is not correct.")
    except AttributeError:
        errors_list.append("STYLESHEETS variable is missing from the configuration file.")

    # For the two variables where the value is not a path, check if the variable exists.
    try:
        c.NAMESPACE
    except AttributeError:
        errors_list.append("NAMESPACE variable is missing from the configuration file.")

    try:
        c.GROUPS
    except AttributeError:
        errors_list.append("GROUPS variable is missing from the configuration file.")

    # The errors list is empty if there were no errors.
    return errors_list


def check_metadata_csv(read_metadata, aips_dir):
    """Verify the content of the metadata.csv is correct

    - Columns are in the required order
    - Departments match ARCHive group codes
    - No AIP is in the CSV more than once
    - The AIPs in the CSV match the folders in the AIPs directory

    Parameters:
        read_metadata : contents of the metadata.csv file, read with the csv library
        aips_dir : the path to the folder which contains the folders to be made into AIPs

    Returns:
        errors_list : a list of errors, or an empty list if there were no errors
    """

    # Starts a list for all encountered errors, so all errors can be checked before returning a result.
    errors_list = []

    # Checks that the CSV header row has the required values (case-insensitive).
    # If the header is not correct, returns the error and does not test the column values.
    header = next(read_metadata)
    header_lowercase = [name.lower() for name in header]
    if header_lowercase != ["department", "collection", "folder", "aip_id", "title", "version"]:
        errors_list.append("The columns in the metadata.csv do not match the required values or order.")
        errors_list.append("Required: Department, Collection, Folder, AIP_ID, Title, Version")
        errors_list.append(f"Current:  {', '.join(header)}")
        errors_list.append("Since the columns are not correct, did not check the column values.")
        return errors_list

    # Makes a list of all values in the department and folder columns to use for testing.
    csv_dept_list = []
    csv_folder_list = []
    for row in read_metadata:
        csv_dept_list.append(row[0])
        csv_folder_list.append(row[2])

    # Checks that the values in the department column match the expected ARCHive groups from the configuration file.
    unique_departments = list(set(csv_dept_list))
    unique_departments.sort()
    for department in unique_departments:
        if department not in c.GROUPS:
            errors_list.append(f"{department} is not an ARCHive group.")

    # The rest of the function tests the folder names.

    # Makes a list of every folder name in the AIPs directory.
    aips_directory_list = []
    for item in os.listdir(aips_dir):
        if os.path.isdir(os.path.join(aips_dir, item)):
            aips_directory_list.append(item)

    # Checks for any folder names that are in the CSV more than once.
    duplicates = [folder for folder in csv_folder_list if csv_folder_list.count(folder) > 1]
    if len(duplicates) > 0:
        unique_duplicates = list(set(duplicates))
        unique_duplicates.sort()
        for duplicate in unique_duplicates:
            errors_list.append(f"{duplicate} is in the metadata.csv folder column more than once.")

    # Checks for any folders that are only in the CSV.
    just_csv = list(set(csv_folder_list) - set(aips_directory_list))
    if len(just_csv) > 0:
        just_csv.sort()
        for aip_folder in just_csv:
            errors_list.append(f"{aip_folder} is in metadata.csv and missing from the AIPs directory.")

    # Checks for any folders that are only in the AIPs directory.
    just_aip_dir = list(set(aips_directory_list) - set(csv_folder_list))
    if len(just_aip_dir) > 0:
        just_aip_dir.sort()
        for aip_folder in just_aip_dir:
            errors_list.append(f"{aip_folder} is in the AIPs directory and missing from metadata.csv.")

    # The errors list is empty if there were no errors.
    return errors_list


def combine_metadata(aip, staging):
    """Make the combined-fits.xml file in the metadata folder, which contains the FITS output for every file in the AIP

    It is moved out of the AIP folder and into the fits-xml folder after the preservation.xml is made.
    Only the FITS XML for each file is kept in the AIP.

    Parameters:
        aip : instance of the AIP class, used for id and log
        staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Makes a new XML object with the root element named combined-fits.
    combo_tree = et.ElementTree(et.Element("combined-fits"))
    combo_root = combo_tree.getroot()

    # Gets each of the FITS documents in the AIP's metadata folder.
    metadata_path = os.path.join(aip.directory, aip.id, "metadata")
    for doc in os.listdir(metadata_path):
        if doc.endswith("_fits.xml"):

            # Makes Python aware of the FITS namespace (it is the default and has no prefix).
            et.register_namespace("", "http://hul.harvard.edu/ois/xml/ns/fits/fits_output")

            # Gets the FITS element and its children and makes it a child of the root, combined-fits.
            try:
                tree = et.parse(os.path.join(metadata_path, doc))
                root = tree.getroot()
                combo_root.append(root)
                aip.log["FITSError"] = "Successfully created combined-fits.xml"
            # Errors: the file is empty, is not XML, or has invalid XML.
            # Moves the AIP to an error folder and does not execute the rest of this function.
            except et.ParseError as error:
                aip.log["FITSError"] = f"Issue when creating combined-fits.xml: {error.msg}"
                aip.log["Complete"] = "Error during processing"
                log(aip.log, aip.directory)
                move_error("combining_fits", os.path.join(aip.directory, aip.id), staging)
                return

    # Saves the combined-fits XML to a file named aip-id_combined-fits.xml in the AIP's metadata folder.
    fits_path = os.path.join(metadata_path, f"{aip.id}_combined-fits.xml")
    combo_tree.write(fits_path, xml_declaration=True, encoding="UTF-8")


def delete_temp(aip, aip_path, logging):
    """Delete temporary files of various types from the AIP folder and optionally make a log of the deleted files

    Temporary files are deleted because they cause errors later in the workflow, especially with bag validation.
    Types of files deleted: DS_Store, Thumbs.db, ends with .tmp, and starts with '.'

    A log is made the first time temporary files are deleted, since they likely came with the accession.
    Later deletions are for temporary files made by the AIP creation process in a Mac and do not need a log.

    Parameters:
         aip : instance of the AIP class, used for directory, id and log
         aip_path : path to the aip folder, either named with the aip_id or aip_id_bag
         logging : True or False, indicating if a deletion log should be made

    Returns: none
    """

    # List of files that were deleted, to save to a log.
    deleted_files = []

    # Checks all files at any level in the AIP folder against the deletion criteria.
    # Deletes DS_Store, Thumbs.db, starts with a dot, or ends with .tmp.
    # Gets information for the deletion log if a log will be made and deletes the file.
    delete_list = [".DS_Store", "._.DS_Store", "Thumbs.db"]
    for root, directories, files in os.walk(aip_path):
        for item in files:
            if item in delete_list or item.endswith(".tmp") or item.startswith("."):
                if logging:
                    path = os.path.join(root, item)
                    date = time.gmtime(os.path.getmtime(path))
                    date_reformatted = f"{date.tm_year}-{date.tm_mon}-{date.tm_mday} {date.tm_hour}:{date.tm_hour}:{date.tm_min}"
                    deleted_files.append([path, item, os.path.getsize(path), date_reformatted])
                os.remove(os.path.join(root, item))

    # If there is logging, creates the deletion log and updates the AIP log.
    # The deletion log contains the path, filename, size in bytes and date/time last modified of every deleted file.
    # If there is no logging, the function is running to delete temp files generated during AIP creation.
    if logging:
        if len(deleted_files) > 0:
            filename = f"{aip.id}_files-deleted_{datetime.today().strftime('%Y-%#m-%#d')}_del.csv"
            with open(os.path.join(aip.directory, aip.id, filename), "w", newline="") as deleted_log:
                deleted_log_writer = csv.writer(deleted_log)
                deleted_log_writer.writerow(["Path", "File Name", "Size (Bytes)", "Date Last Modified"])
                for file_data in deleted_files:
                    deleted_log_writer.writerow(file_data)
            aip.log["Deletions"] = "File(s) deleted (see log)"
        else:
            aip.log["Deletions"] = "No files deleted"


def extract_metadata(aip):
    """Extract technical metadata from the files in the objects folder using FITS and saves to metadata folder

    Parameters:
         aip : instance of the AIP class, used for directory, id, and log

    Returns: none
    """

    # Runs FITS on the files in the AIP's objects folder and saves the output to its metadata folder.
    # The FITS output is named with the original file name. If there is more than one file anywhere
    # within the objects folder with the same name, FITS adds a number to the duplicates, for example:
    # file.ext.fits.xml, file.ext-1.fits.xml, file.ext-2.fits.xml
    objects = os.path.join(aip.directory, aip.id, "objects")
    metadata = os.path.join(aip.directory, aip.id, "metadata")
    fits_output = subprocess.run(f'"{c.FITS}" -r -i "{objects}" -o "{metadata}"',
                                 shell=True, stderr=subprocess.PIPE)

    # If there were any tool error messages from FITS, saves those to a log in the AIP's metadata folder.
    # Processing on the AIP continues, since typically other tools still work.
    if fits_output.stderr:
        with open(os.path.join(metadata, f"{aip.id}_fits-tool-errors_fitserr.txt"), "w") as fits_errors:
            fits_errors.write(fits_output.stderr.decode("utf-8"))
        aip.log["FITSTool"] = "FITS tools generated errors (saved to metadata folder)"
    else:
        aip.log["FITSTool"] = "No FITS tools errors"

    # Renames the FITS output to the UGA Libraries' metadata naming convention (filename_fits.xml).
    for item in os.listdir(metadata):
        if item.endswith(".fits.xml"):
            new_name = item.replace(".fits", "_fits")
            os.rename(os.path.join(metadata, item), os.path.join(metadata, new_name))


def log(log_data, aips_dir):
    """Save the result about each step done on an AIP to a CSV file

    Information is saved to the log after the AIP either finishes processing or encounters an anticipated error.

    Parameters:
        log_data : "header" or dictionary with log information for the AIP
        aips_dir : the path to the folder which contains the folders to be made into AIPs

    Returns: none
    """

    # Formats the data for this row in the log CSV as a list.
    # For the header, uses default values.
    # In all other cases, log_data is a dictionary, with one key per column in the log.
    if log_data == "header":
        log_row = ["Time Started", "AIP ID", "Files Deleted", "Objects Folder",
                   "Metadata Folder", "FITS Tool Errors", "FITS Combination Errors", "Preservation.xml Made",
                   "Preservation.xml Valid", "Bag Valid", "Package Errors", "Manifest Errors", "Processing Complete"]
    else:
        log_row = [log_data["Started"], log_data["AIP"], log_data["Deletions"],
                   log_data["ObjectsError"], log_data["MetadataError"], log_data["FITSTool"], log_data["FITSError"],
                   log_data["PresXML"], log_data["PresValid"], log_data["BagValid"], log_data["Package"],
                   log_data["Manifest"], log_data["Complete"]]

    # Saves the data for the row to the log CSV.
    with open(os.path.join(aips_dir, "aip_log.csv"), "a", newline="") as log_file:
        log_writer = csv.writer(log_file)
        log_writer.writerow(log_row)


def make_bag(aip):
    """Bag the AIP, with md5 and sha256 manifests, and rename the AIP folder to add "_bag" to the end

    Parameters:
         aip : instance of the AIP class, used for id

    Returns: none
    """

    # Deletes temporary files. These can be re-generated during the AIP creation process.
    aip_path = os.path.join(aip.directory, aip.id)
    delete_temp(aip, aip_path, logging=False)

    # Bags the AIP. To save time, BMAC AV only generates md5 checksums.
    if aip.type == "av" and aip.department == "bmac":
        bagit.make_bag(aip_path, checksums=["md5"])
    else:
        bagit.make_bag(aip_path, checksums=["md5", "sha256"])

    # Renames the AIP folder to add _bag (common naming convention for the standard).
    os.replace(aip_path, os.path.join(aip.directory, f"{aip.id}_bag"))


def make_cleaned_fits_xml(aip, staging):
    """Make a simplified version of the combined-fits.xml in the metadata folder

    The cleaned FITS makes the format information is easier to aggregate.
    It is deleted after the preservation.xml is made.

    Parameters:
        aip : instance of the AIP class, used for directory, id and log
        staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Uses saxon and a stylesheet to make the cleaned-fits.xml from the combined-fits.xml.
    input_file = os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_combined-fits.xml")
    stylesheet = os.path.join(c.STYLESHEETS, "fits-cleanup.xsl")
    output_file = os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_cleaned-fits.xml")
    saxon_output = subprocess.run(f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{input_file}" '
                                  f'-xsl:"{stylesheet}" -o:"{output_file}"',
                                  stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, logs the event and moves the AIP to an error folder.
    if saxon_output.stderr:
        error_msg = saxon_output.stderr.decode("utf-8")
        aip.log["PresXML"] = f"Issue when creating cleaned-fits.xml. Saxon error: {error_msg}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        move_error("cleaned_fits_saxon_error", os.path.join(aip.directory, aip.id), staging)


def make_output_directories(staging, aip_type):
    """Make the directories for script outputs, if they don't already exist, in AIP staging

    Parameters:
        staging : path to the aip_staging folder from configuration.py
        aip_type : AIP type (av, general, web)

    Returns: none
    """

    # Determine the output directories needed, based on the AIP type.
    if aip_type == 'av':
        output_directories = ['aips-already-on-ingest-server', 'aips-ready-to-ingest', 'fits-xmls',
                              'md5-manifests-for-aips', 'mediainfo-xmls/mediainfo-raw-output',
                              'mediainfo-xmls/pbcore2-xml', 'movs-to-bag', 'preservation-xmls']
    else:
        output_directories = ['aips-ready-to-ingest', 'fits-xmls', 'preservation-xmls']
    # Makes the output directories, if they don't already exist.
    # In some cases, these folders are never deleted and contain output from all AIPs in ARCHive.
    for directory in output_directories:
        directory_path = os.path.join(staging, directory)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)


def make_preservation_xml(aip, staging):
    """Make the preservation.xml from the cleaned FITS XML in the metadata folder

    Parameters:
        aip : instance of the AIP class, used for collection_id, department, directory, id, log, title, and version
        staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Uses saxon and a stylesheet to make the preservation.xml file from the cleaned-fits.xml.
    input_file = os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_cleaned-fits.xml")
    stylesheet = os.path.join(c.STYLESHEETS, "fits-to-preservation.xsl")
    output_file = os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_preservation.xml")
    args = f'collection-id="{aip.collection_id}" aip-id="{aip.id}" aip-title="{aip.title}" ' \
           f'department="{aip.department}" version={aip.version} ns={c.NAMESPACE}'
    saxon_output = subprocess.run(f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{input_file}" '
                                  f'-xsl:"{stylesheet}" -o:"{output_file}" {args}',
                                  stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, logs the event and moves the AIP to an error folder.
    if saxon_output.stderr:
        error_msg = saxon_output.stderr.decode("utf-8")
        aip.log["PresXML"] = f"Issue when creating preservation.xml. Saxon error: {error_msg}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        move_error("pres_xml_saxon_error", os.path.join(aip.directory, aip.id), staging)
        return


def manifest(aip, staging, ingest):
    """Calculate the MD5 checksum for the AIP and add it to the department's manifest in the aips-to-ingest folder

    One manifest is made for each department so that AIPs may be made for multiple departments simultaneously.
    One manifest per department is needed to ingest AIPs into our digital preservation system.

    Parameters:
         aip : instance of the AIP class, used for department, id, log, size, and to_zip
         staging : path to the aip_staging folder from configuration.py
         ingest : path to the ARCHive ingest server folder from configuration.py

    Returns: none
    """

    # Makes the path to the packaged AIP, which is different depending on if it is zipped or not.
    aip_path = os.path.join(staging, "aips-ready-to-ingest", f"{aip.id}_bag.{aip.size}.tar")
    if aip.to_zip is True:
        aip_path = aip_path + ".bz2"

    # Checks if the tar/zip is present in the aips-to-ingest directory.
    # If it isn't, due to errors from package(), logs the event and does not complete the rest of the function.
    if not os.path.exists(aip_path):
        aip.log["Manifest"] = f"Tar/zip file '{aip_path}' not in aips-ready-for-ingest folder"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        return

    # Calculates the MD5 of the packaged AIP.
    md5deep_result = subprocess.run(f'"{c.MD5DEEP}" -br "{aip_path}"',
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # If md5deep has an error, logs the event and does not execute the rest of this function.
    if md5deep_result.stderr:
        error_msg = md5deep_result.stderr.decode("utf-8")
        aip.log["Manifest"] = f"Issue when generating MD5. md5deep error: {error_msg}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        return

    # Adds the md5 and AIP filename to the appropriate manifest in staging.
    # Initial output of md5deep is b'md5_value  filename.ext\r\n'
    # Converts to a string and remove the \r linebreak to format the manifest text file as required by ARCHive.
    manifest_name = f'manifest_{os.path.basename(aip.directory)}_{aip.department}_{datetime.now().strftime("%Y-%m-%d")}.txt'
    if aip.type == "av":
        manifest_path = os.path.join(staging, "md5-manifests-for-aips", manifest_name)
    else:
        manifest_path = os.path.join(staging, "aips-ready-to-ingest", manifest_name)
    with open(manifest_path, "a", encoding="utf-8") as manifest_file:
        manifest_file.write(md5deep_result.stdout.decode("UTF-8").replace("\r", ""))

    # For AV, copies to ARCHive ingest to be ready to schedule.
    # TODO: is there an rsync-like option for Windows for the other workflows? Or just use Python?
    if aip.type == 'av':
        rsync_result = subprocess.run(f'rsync -v --progress {aip_path} {ingest}', stderr=subprocess.PIPE, shell=True)

        # If copied correctly, move to a different folder on AIPs staging. Otherwise, move to an error folder.
        if not rsync_result.stderr:
            aip_zip_name = os.path.basename(aip_path)
            shutil.move(aip_path, f'{staging}/aips-already-on-ingest-server/{aip_zip_name}')
        else:
            move_error('copy_to_ingest_failed', aip_path, staging)
            error_msg = rsync_result.stderr.decode("utf-8")
            aip.log["Manifest"] = (f"Successfully added AIP to manifest. "
                                   f"Issue when copying to ingest. rsync error: {error_msg}")
            aip.log["Complete"] = "Error during processing"
            log(aip.log, aip.directory)
            return

    # Logs the success of adding the AIP to the manifest and of AIP creation (this is the last step).
    aip.log["Manifest"] = "Successfully added AIP to manifest"
    aip.log["Complete"] = "Successfully completed processing"
    log(aip.log, aip.directory)


def move_error(error_name, aip_path, staging):
    """Move the AIP folder to an error folder, named with the error type

    The AIP is moved so the rest of the workflow steps are not attempted on it.

    Parameters:
        error_name : the name of the error folder
        aip_path : the path of the AIP folder with the error
        staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Makes the error folder, if it does not already exist.
    error_path = os.path.join(staging, "aips-with-errors", error_name)
    if not os.path.exists(error_path):
        os.makedirs(error_path)

    # Moves the AIP to the error folder.
    os.replace(aip_path, os.path.join(error_path, os.path.basename(aip_path)))


def organize_xml(aip, staging):
    """Organize the XML files after the preservation.xml is successfully made

    - A copy of the preservation.xml is made in the preservation-xml folder
    - The combined-fits.xml is moved to the fits-xml folder
    - The cleaned-fits.xml is deleted

    Parameters:
         aip : instance of the AIP class, used for id
         staging : path to the aip_staging folder from configuration.py, where copies are saved
    Returns: none
    """

    # Copies the preservation.xml file to the preservation-xml folder for staff reference.
    shutil.copy2(os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_preservation.xml"),
                 os.path.join(staging, "preservation-xmls"))

    # Moves the combined-fits.xml file to the fits-xml folder for staff reference.
    # Only the FITS for individual files is kept in the metadata folder.
    os.replace(os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_combined-fits.xml"),
               os.path.join(staging, "fits-xmls", f"{aip.id}_combined-fits.xml"))

    # Deletes the cleaned-fits.xml file because it is a temporary file.
    os.remove(os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_cleaned-fits.xml"))


def package(aip, staging):
    """Tar and zip (optional) the AIP, rename it to include the size, and save it to the aips-ready-to-ingest folder

    AIPs may not be zipped if zipping is time-consuming and does not save much space. They must be tarred.
    The unzipped size is included so the preservation system can determine if there is room to unzip it during ingest.

    Parameters:
         aip : instance of the AIP class, used for directory, id, log, size, and to_zip
         staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Gets the operating system, since the tar and zip commands are different for Windows and Mac/Linux.
    operating_system = platform.system()

    # Makes variables for the AIP folder name and AIP full path.
    aip_bag = f"{aip.id}_bag"
    bag_path = os.path.join(aip.directory, aip_bag)

    # Deletes temporary files. These can be re-generated during the AIP creation process.
    delete_temp(aip, bag_path, logging=False)

    # Gets the total size of the bag:
    # sum of the bag payload (data folder) from bag-info.txt and the size of the bag metadata files.
    # It saves time to use the bag payload instead of recalculating the size of a large data folder.
    try:
        bag_info = open(os.path.join(bag_path, "bag-info.txt"), "r")
    except FileNotFoundError:
        aip.log["Package"] = f"Could not tar. Bag not in expected location: {bag_path}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        return
    bag_size = 0
    for line in bag_info:
        if line.startswith("Payload-Oxum"):
            payload = line.split()[1]
            bag_size += float(payload)
    for file in os.listdir(bag_path):
        if file.endswith(".txt"):
            bag_size += os.path.getsize(os.path.join(bag_path, file))
    bag_info.close()
    bag_size = int(bag_size)

    # Tars the file, using the command appropriate for the operating system.
    tar_path = os.path.join(staging, 'aips-ready-to-ingest', f"{aip_bag}.tar")
    if operating_system == "Windows":
        # Does not print the progress to the terminal (stdout), which is a lot of text. [subprocess.DEVNULL]
        tar_output = subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -ttar a "{tar_path}" "{bag_path}"',
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
        # If there is an error, saves the error to the log and does not complete the rest of the function for this AIP.
        # Cannot move it to an error folder because getting a permissions error.
        if not tar_output.stderr == b"":
            error_msg = tar_output.stderr.decode("utf-8")
            aip.log["Package"] = f"Could not tar. 7zip error: {error_msg}"
            aip.log["Complete"] = "Error during processing"
            log(aip.log, aip.directory)
            return
    else:
        subprocess.run(f'tar -C "{bag_path}" -cf "{tar_path}" .', shell=True)

    # Renames the file to include the size.
    tar_size_path = os.path.join(staging, "aips-ready-to-ingest", f"{aip_bag}.{bag_size}.tar")
    os.replace(tar_path, tar_size_path)

    # Updates the size in the AIP object, so it can be used by the manifest() function later.
    aip.size = bag_size

    # If the AIP should be zipped (if the value of to_zip is true),
    # Zips (bz2) the tar file, using the command appropriate for the operating system.
    if aip.to_zip is True:
        if operating_system == "Windows":
            # Does not print the progress to the terminal (stdout), which is a lot of text.
            subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -tbzip2 a -aoa "{tar_size_path}.bz2" "{tar_size_path}"',
                           stdout=subprocess.DEVNULL, shell=True)
        else:
            subprocess.run(f'bzip2 "{tar_size_path}"', shell=True)

        # Deletes the tar version. Just want the tarred and zipped version.
        # For Mac/Linux, the bzip2 command overwrites the tar file so this step is unnecessary.
        if operating_system == "Windows":
            os.remove(tar_size_path)

    # Updates the log with success.
    aip.log["Package"] = "Successfully made package"


def structure_directory(aip, staging):
    """Make the AIP directory structure (objects and metadata folders) and move the digital objects into those folders

    Anything not recognized as metadata is moved into the objects folder.
    If the digital objects are already organized into folders,
    that directory structure is maintained within the objects folder.

    Parameters:
         aip : instance of the AIP class, used for directory, workflow, department, id, and log
         staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Makes the objects folder within the AIP folder, if it doesn't exist.
    # If it does, moves the AIP to an error folder so the original directory structure is not altered.
    aip_path = os.path.join(aip.directory, aip.id)
    try:
        os.mkdir(os.path.join(aip_path, "objects"))
        aip.log["ObjectsError"] = "Successfully created objects folder"
    except FileExistsError:
        aip.log["ObjectsError"] = "Objects folder already exists in original files"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        move_error("objects_folder_exists", aip_path, staging)
        return

    # Makes the metadata folders within the AIP folder, if it doesn't exist.
    # If it does, moves the AIP to an error folder so the original directory structure is not altered.
    try:
        os.mkdir(os.path.join(aip_path, "metadata"))
        aip.log["MetadataError"] = "Successfully created metadata folder"
    except FileExistsError:
        aip.log["MetadataError"] = "Metadata folder already exists in original files"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        move_error("metadata_folder_exists", aip_path, staging)
        return

    # Moves DPX files to the objects folder.
    # DPX files are already in bags, so have to navigate to the data folder to find the content to move into objects.
    if aip.workflow == 'dpx':
        for item in os.listdir(os.path.join(aip_path, 'data')):
            if os.path.isdir(os.path.join(aip_path, 'data', item)):
                shutil.copytree(os.path.join(aip_path, 'data', item), os.path.join(aip_path, 'objects', f'{item}-dpx'))
            elif item.endswith('.cue'):
                os.replace(os.path.join(aip_path, 'data', item), os.path.join(aip_path, 'objects', item))
            elif item.endswith('.mov'):
                shutil.copy2(os.path.join(aip_path, 'data', item), os.path.join(staging, 'movs-to-bag'))
                os.replace(os.path.join(aip_path, 'data', item), os.path.join(aip_path, 'objects', item))
            elif item.endswith('.wav'):
                os.replace(os.path.join(aip_path, 'data', item),
                           os.path.join(aip_path, 'objects', f'{pathlib.Path(item).stem}-dpx.wav'))
        # Deletes the bag metadata files and data folder, now that the rest is organized into the AIP directory.
        for bag_metadata_file in ('bag-info.txt', 'bagit.txt', 'manifest-md5.txt', 'tagmanifest-md5.txt'):
            os.remove(os.path.join(aip_path, bag_metadata_file))
        shutil.rmtree(os.path.join(aip_path, 'data'))

    # Moves any metadata files to the metadata folder and then the rest to the objects folder, with renaming as needed.
    # Metadata files are matched as specifically as possible to reduce the risk of incorrect identifications.
    web_metadata = ("_coll.csv", "_collscope.csv", "_crawldef.csv", "_crawljob.csv", "_seed.csv", "_seedscope.csv")
    for item in os.listdir(aip_path):
        if item in ('metadata', 'objects'):
            continue
        item_path = os.path.join(aip_path, item)
        # AV metadata files.
        av_metadata = (".qctools.mkv", ".qctools.xml.gz", ".framemd5", ".srt")
        if aip.type == "av" and item.endswith(av_metadata):
            os.replace(item_path, os.path.join(aip_path, "metadata", f"bmac_{item}"))
        # Deletion log, created by the script when deleting temp files.
        elif item.startswith(f"{aip.id}_files-deleted_"):
            os.replace(item_path, os.path.join(aip_path, "metadata", item))
        # Metadata file used by Emory with disk images.
        elif aip.department == "emory" and item.startswith("EmoryMD"):
            os.replace(item_path, os.path.join(aip_path, "metadata", item))
        # Website metadata files from downloading WARCs from Archive-It.
        # Hargrett and Russell both have -web- in the AIP ID, but MAGIL does not and can only check for the department.
        elif "-web-" in aip.id and item.endswith(web_metadata):
            os.replace(item_path, os.path.join(aip_path, "metadata", item))
        elif aip.department == "magil" and item.endswith(web_metadata):
            os.replace(item_path, os.path.join(aip_path, "metadata", item))
        # MXF files (renaming required, different from other AV)
        elif aip.department == "bmac" and aip.workflow == "mxf":
            os.replace(item_path, os.path.join(aip_path, "objects", f"bmac_wsb-video_{item.lower()}"))
        # Moves all other BMA files to the objects folder, with renaming.
        elif aip.department == "bmac":
            os.replace(item_path, os.path.join(aip_path, "objects", f"bmac_{item}"))
        # Moves all remaining files and folders to the objects folder.
        else:
            os.replace(item_path, os.path.join(aip_path, "objects", item))


def validate_bag(aip, staging):
    """Validate the AIP's bag

    Parameters:
         aip : instance of the AIP class, used for id and log
         staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Validate the bag with bagit, and save an errors in a separate log.
    bag_path = os.path.join(aip.directory, f"{aip.id}_bag")
    new_bag = bagit.Bag(bag_path)
    try:
        new_bag.validate()
        aip.log["BagValid"] = f"Bag valid on {datetime.now()}"
    except bagit.BagValidationError as errors:
        aip.log["BagValid"] = "Bag not valid (see log in bag_not_valid error folder)"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        move_error("bag_not_valid", bag_path, staging)
        # Error log is formatted to be easier to read (one error per line) if error information is in details.
        # Otherwise, the entire error output is saved to the log in the errors folder alongside the AIP folder.
        log_path = os.path.join(staging, "aips-with-errors", "bag_not_valid", f"{aip.id}_bag_validation.txt")
        with open(log_path, "w") as log_path:
            if errors.details:
                for error_type in errors.details:
                    log_path.write(str(error_type) + "\n")
            else:
                log_path.write(str(errors))


def validate_preservation_xml(aip, staging):
    """Validate the preservation.xml file against UGA's requirements

    Parameters:
         aip : instance of the AIP class, used for id and log
         staging : path to the aip_staging folder from configuration.py

    Returns: none
    """

    # Uses xmllint and an XSD file to validate the preservation.xml.
    input_file = os.path.join(aip.directory, aip.id, "metadata", f"{aip.id}_preservation.xml")
    stylesheet = os.path.join(c.STYLESHEETS, "preservation.xsd")
    xmllint_output = subprocess.run(f'xmllint --noout -schema "{stylesheet}" "{input_file}"',
                                    stderr=subprocess.PIPE, shell=True)

    # If the preservation.xml file was not made in the expected location, moves the AIP to an error folder.
    # If it was made, updates the log with the success.
    validation_result = xmllint_output.stderr.decode("utf-8")
    if "failed to load" in validation_result:
        aip.log["PresXML"] = f"Preservation.xml was not created. xmllint error: {validation_result}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        move_error("preservationxml_not_found", os.path.join(aip.directory, aip.id), staging)
        return
    else:
        aip.log["PresXML"] = "Successfully created preservation.xml"

    # If the preservation.xml does not meet the requirements, moves the AIP to an error folder.
    # The validation output is saved to a file in the error folder for review.
    # If it is valid, updates the log with the success.
    if "fails to validate" in validation_result:
        aip.log["PresValid"] = "Preservation.xml is not valid (see log in error folder)"
        aip.log["Complete"] = "Error during processing"
        log(aip.log, aip.directory)
        move_error("preservationxml_not_valid", os.path.join(aip.directory, aip.id), staging)
        log_path = os.path.join(staging, "aips-with-errors", "preservationxml_not_valid",
                                f"{aip.id}_presxml_validation.txt")
        with open(log_path, "w") as validation_log:
            for line in validation_result.split("\r"):
                validation_log.write(line + "\n")
        return
    else:
        aip.log["PresValid"] = f"Preservation.xml valid on {datetime.now()}"
