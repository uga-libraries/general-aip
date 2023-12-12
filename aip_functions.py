"""
Functions used to make AIPs from folders of digital objects that are ready for ingest into the
UGA Libraries' digital preservation system (ARCHive).
"""

import csv
import datetime
import os
import platform
import shutil
import subprocess
import time
import xml.etree.ElementTree as et
import bagit
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


def check_arguments(arguments):
    """Verifies that all the arguments received are correct and assigns values to
    variables aips_directory, to_zip, and aip_metadata_csv.
    Returns the variables and a list of errors in a tuple."""

    # Starts a list for all encountered errors, so all errors can be checked before returning a result,
    # and the two variables assigned from arguments are set to None.
    # These are updated to the correct value from the arguments, if they are provided.
    errors_list = []
    aips_directory = None
    to_zip = None

    # Checks if arguments were given, besides the default of script name.
    # If not, saves an error. It will not check for the other arguments.
    if len(arguments) == 1:
        errors_list.append("AIPs directory argument is missing.")

    # Assigns the required script argument to the aips_directory variable, if it is a valid directory.
    # If not, saves an error.
    if len(arguments) > 1:
        if os.path.exists(arguments[1]):
            aips_directory = arguments[1]
        else:
            errors_list.append("AIPs directory argument is not a valid directory.")

    # Assigns the value of the to_zip value based on the optional argument.
    # If it is missing, value is True. If it is no-zip, value is False. If it is anything else, value stays None.
    if len(arguments) > 2:
        if arguments[2] == "no-zip":
            to_zip = False
        else:
            errors_list.append("Unexpected value for the second argument. If provided, should be 'no-zip'.")
    else:
        to_zip = True

    # Generates the path to the required metadata file and verifies it is present.
    # Only tests if there is a value for aips_directory, which is part of the path.
    if aips_directory:
        aip_metadata_csv = os.path.join(aips_directory, "metadata.csv")
        if not os.path.exists(aip_metadata_csv):
            aip_metadata_csv = None
            errors_list.append("Missing the required file metadata.csv in the AIPs directory.")
    else:
        aip_metadata_csv = None
        errors_list.append("Cannot check for the metadata.csv because the AIPs directory has an error.")

    # Returns the variables and errors list in a tuple.
    # The errors list is empty if there where no errors.
    return aips_directory, to_zip, aip_metadata_csv, errors_list


def check_configuration():
    """Verifies all the expected variables are in the configuration file and paths are valid if they are a path.
    Returns a list of errors or an empty list if there are no errors."""

    # Starts a list for all encountered errors, so all errors can be checked before returning a result.
    errors_list = []

    # For the 4 variables with a value that is a path, checks if the variable exists.
    # If so check if the path is valid.
    # Either error (doesn't exist or not valid) is added to the errors list.
    try:
        if not os.path.exists(c.FITS):
            errors_list.append(f"FITS path '{c.FITS}' is not correct.")
    except AttributeError:
        errors_list.append("FITS variable is missing from the configuration file.")

    try:
        if not os.path.exists(c.SAXON):
            errors_list.append(f"SAXON path '{c.SAXON}' is not correct.")
    except AttributeError:
        errors_list.append("SAXON variable is missing from the configuration file.")

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

    # For the 2 variables where the value is not a path, check if the variable exists.
    # If not, add to the error list.
    try:
        c.NAMESPACE
    except AttributeError:
        errors_list.append("NAMESPACE variable is missing from the configuration file.")

    try:
        c.GROUPS
    except AttributeError:
        errors_list.append("GROUPS variable is missing from the configuration file.")

    # Returns the errors list. If there were no errors, it will be empty.
    return errors_list


def check_metadata_csv(read_metadata):
    """Verifies that the columns are in the required order.
    If so, verifies that the departments match ARCHive group codes
    and that the AIP list in the CSV matches the folders in the AIPs directory.
    Returns a list of errors or an empty list if there are no errors. """

    # Starts a list for all encountered errors, so all errors can be checked before returning a result.
    errors_list = []

    # Does a case insensitive comparison of the CSV header row with the required values.
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

    # Tests the values in the department column match the expected ARCHive groups from the configuration file.
    # Saves any that don't match to the errors list.
    unique_departments = list(set(csv_dept_list))
    unique_departments.sort()
    for department in unique_departments:
        if department not in c.GROUPS:
            errors_list.append(f"{department} is not an ARCHive group.")

    # The rest of the function tests the folder names.

    # Makes a list of every folder name in the AIPs directory.
    aips_directory_list = []
    for item in os.listdir("."):
        if os.path.isdir(item):
            aips_directory_list.append(item)

    # Finds any folder names that are in the CSV more than once and adds them to the error list.
    duplicates = [folder for folder in csv_folder_list if csv_folder_list.count(folder) > 1]
    if len(duplicates) > 0:
        unique_duplicates = list(set(duplicates))
        unique_duplicates.sort()
        for duplicate in unique_duplicates:
            errors_list.append(f"{duplicate} is in the metadata.csv folder column more than once.")

    # Finds any AIPs that are only in the CSV and adds them to the error list.
    just_csv = list(set(csv_folder_list) - set(aips_directory_list))
    if len(just_csv) > 0:
        just_csv.sort()
        for aip in just_csv:
            errors_list.append(f"{aip} is in metadata.csv and missing from the AIPs directory.")

    # Finds any AIPs that are only in the AIPs directory and adds them to the error list.
    just_aip_dir = list(set(aips_directory_list) - set(csv_folder_list))
    if len(just_aip_dir) > 0:
        just_aip_dir.sort()
        for aip in just_aip_dir:
            errors_list.append(f"{aip} is in the AIPs directory and missing from metadata.csv.")

    # Returns the errors list. If there were no errors, it will be empty.
    return errors_list


def combine_metadata(aip):
    """Creates a single XML file that combines the FITS output for every file in the AIP. """

    # Makes a new XML object with the root element named combined-fits.
    combo_tree = et.ElementTree(et.Element("combined-fits"))
    combo_root = combo_tree.getroot()

    # Gets each of the FITS documents in the AIP's metadata folder.
    for doc in os.listdir(os.path.join(aip.id, "metadata")):
        if doc.endswith("_fits.xml"):

            # Makes Python aware of the FITS namespace.
            et.register_namespace("", "http://hul.harvard.edu/ois/xml/ns/fits/fits_output")

            # Gets the FITS element and its children and makes it a child of the root, combined-fits.
            try:
                tree = et.parse(os.path.join(aip.id, "metadata", doc))
                root = tree.getroot()
                combo_root.append(root)
                aip.log["FITSError"] = "Successfully created combined-fits.xml"
            # Errors: the file is empty, is not XML, or has invalid XML.
            # Moves the AIP to an error folder and does not execute the rest of this function.
            except et.ParseError as error:
                aip.log["FITSError"] = f"Issue when creating combined-fits.xml: {error.msg}"
                aip.log["Complete"] = "Error during processing"
                log(aip.log)
                move_error("combining_fits", aip.id)
                return

    # Saves the combined-fits XML to a file named aip-id_combined-fits.xml in the AIP's metadata folder.
    fits_path = os.path.join(aip.id, "metadata", f"{aip.id}_combined-fits.xml")
    combo_tree.write(fits_path, xml_declaration=True, encoding="UTF-8")


def delete_temp(aip):
    """Deletes temporary files of various types from anywhere within the AIP folder because they cause errors later
    in the workflow, especially with bag validation. Creates a log of the deleted files as a record of actions taken
    on the AIP during processing. This is especially important if there are large files that result in a noticeable
    change in size after making the AIP. """

    # List of files to be deleted where the filename can be matched in its entirety.
    delete_list = [".DS_Store", "._.DS_Store", "Thumbs.db"]

    # List of files that were deleted, to save to a log.
    deleted_files = []

    # Checks all files at any level in the AIP folder against deletion criteria.
    # Deletes: DS_Store, Thumbs.db, starts with a dot, or ends with .tmp.
    # Gets information for the deletion log and then deletes the file.
    for root, directories, files in os.walk(aip.id):
        for item in files:
            if item in delete_list or item.endswith(".tmp") or item.startswith("."):
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
        with open(os.path.join(aip.id, filename), "w", newline="") as deleted_log:
            deleted_log_writer = csv.writer(deleted_log)
            deleted_log_writer.writerow(["Path", "File Name", "Size (Bytes)", "Date Last Modified"])
            for file_data in deleted_files:
                deleted_log_writer.writerow(file_data)
        aip.log["Deletions"] = "File(s) deleted"
    else:
        aip.log["Deletions"] = "No files deleted"


def extract_metadata(aip):
    """Extracts technical metadata from the files in the objects folder using FITS. """

    # Runs FITS on the files in the AIP's objects folder and saves the output to it's metadata folder.
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


def log(log_data):
    """Saves information about each step done on an AIP to a CSV file.
    Information is stored in a dictionary in the AIP instance
    and is saved to the log after the AIP either finishes processing or encounters an anticipated error."""

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
    with open(os.path.join("", "aip_log.csv"), "a", newline="") as log_file:
        log_writer = csv.writer(log_file)
        log_writer.writerow(log_row)


def make_bag(aip):
    """Bags the AIP, using md5 and sha256 checksums,
    and renames the AIP folder to add "_bag" to the end."""

    bagit.make_bag(aip.id, checksums=["md5", "sha256"])
    os.replace(aip.id, f"{aip.id}_bag")


def make_cleaned_fits_xml(aip):
    """Makes a simplified version of the combined fits XML so the format information is easier to aggregate.
    It is saved in the AIP's metadata folder and deleted after the preservation.xml is made."""

    # Uses saxon and a stylesheet to make the cleaned-fits.xml from the combined-fits.xml.
    input_file = os.path.join(aip.id, "metadata", f"{aip.id}_combined-fits.xml")
    stylesheet = os.path.join(c.STYLESHEETS, "fits-cleanup.xsl")
    output_file = os.path.join(aip.id, "metadata", f"{aip.id}_cleaned-fits.xml")
    saxon_output = subprocess.run(f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{input_file}" '
                                  f'-xsl:"{stylesheet}" -o:"{output_file}"',
                                  stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, moves the AIP to an error folder.
    if saxon_output.stderr:
        error_msg = saxon_output.stderr.decode("utf-8")
        aip.log["PresXML"] = f"Issue when creating cleaned-fits.xml. Saxon error: {error_msg}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        move_error("cleaned_fits_saxon_error", aip.id)


def make_output_directories():
    """Makes the directories used to store script outputs, if they don't already exist,
    in the parent folder of the AIPs directory."""

    output_directories = ["aips-to-ingest", "fits-xml", "preservation-xml"]

    for directory in output_directories:
        directory_path = os.path.join("", directory)
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)


def make_preservation_xml(aip):
    """Makes the preservation XML (PREMIS and Dublin Core metadata) from the cleaned FITS XML.
    It is saved in the AIP's metadata folder."""

    # Uses saxon and a stylesheet to make the preservation.xml file from the cleaned-fits.xml.
    input_file = os.path.join(aip.id, "metadata", f"{aip.id}_cleaned-fits.xml")
    stylesheet = os.path.join(c.STYLESHEETS, "fits-to-preservation.xsl")
    output_file = os.path.join(aip.id, "metadata", f"{aip.id}_preservation.xml")
    args = f'collection-id="{aip.collection_id}" aip-id="{aip.id}" aip-title="{aip.title}" ' \
           f'department="{aip.department}" version={aip.version} ns={c.NAMESPACE}'
    saxon_output = subprocess.run(f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{input_file}" '
                                  f'-xsl:"{stylesheet}" -o:"{output_file}" {args}',
                                  stderr=subprocess.PIPE, shell=True)

    # If saxon has an error, moves the AIP to an error folder.
    if saxon_output.stderr:
        error_msg = saxon_output.stderr.decode("utf-8")
        aip.log["PresXML"] = f"Issue when creating preservation.xml. Saxon error: {error_msg}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        move_error("pres_xml_saxon_error", aip.id)
        return


def manifest(aip):
    """Uses md5deep to calculate the MD5 for the AIP and adds it to the manifest for that department
    in the aips-to-ingest folder. Each department has a separate manifest so AIPs for multiple departments
    may be created simultaneously."""

    # Makes the path to the packaged AIP, which is different depending on if it is zipped or not.
    aip_path = os.path.join("", "aips-to-ingest", f"{aip.id}_bag.{aip.size}.tar")
    if aip.to_zip is True:
        aip_path = aip_path + ".bz2"

    # Checks if the tar/zip is present in the aips-to-ingest directory.
    # If it isn't, due to errors from package(), does not complete the rest of the function.
    if not os.path.exists(aip_path):
        aip.log["Manifest"] = "Tar/zip file not in aips-to-ingest folder"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        return

    # Calculates the MD5 of the packaged AIP.
    md5deep_output = subprocess.run(f'"{c.MD5DEEP}" -br "{aip_path}"',
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # If md5deep has an error, does not execute the rest of this function.
    if md5deep_output.stderr:
        error_msg = md5deep_output.stderr.decode("utf-8")
        aip.log["Manifest"] = f"Issue when generating MD5. md5deep error: {error_msg}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        return

    # Adds the md5 and AIP filename to the department's manifest in the aips-to-ingest folder.
    # Initial output of md5deep is b'md5_value  filename.ext\r\n'
    # Converts to a string and remove the \r linebreak to format the manifest text file as required by ARCHive.
    manifest_path = os.path.join("", "aips-to-ingest", f"manifest_{aip.department}.txt")
    with open(manifest_path, "a", encoding="utf-8") as manifest_file:
        manifest_file.write(md5deep_output.stdout.decode("UTF-8").replace("\r", ""))

    # Logs the success of adding the AIP to the manifest and of processing (this is the last step).
    aip.log["Manifest"] = "Successfully added AIP to manifest"
    aip.log["Complete"] = "Successfully completed processing"
    log(aip.log)


def move_error(error_name, item):
    """Moves the AIP folder to an error folder, named with the error type,
    so the rest of the workflow steps are not completed on it. """

    # Makes the error folder, if it does not already exist.
    # Error folders are in the folder "errors", which is in the parent folder of the AIPs directory.
    error_path = os.path.join("", "errors", error_name)
    if not os.path.exists(error_path):
        os.makedirs(error_path)

    # Moves the AIP to the error folder.
    os.replace(item, os.path.join(error_path, item))


def organize_xml(aip):
    """After the preservation.xml is successfully made, organizes the resulting XML files."""

    # Copies the preservation.xml file to the preservation-xml folder for staff reference.
    shutil.copy2(os.path.join(aip.id, "metadata", f"{aip.id}_preservation.xml"),
                 os.path.join("", "preservation-xml"))

    # Moves the combined-fits.xml file to the fits-xml folder for staff reference.
    os.replace(os.path.join(aip.id, "metadata", f"{aip.id}_combined-fits.xml"),
               os.path.join("", "fits-xml", f"{aip.id}_combined-fits.xml"))

    # Deletes the cleaned-fits.xml file because it is a temporary file.
    os.remove(os.path.join(aip.id, "metadata", f"{aip.id}_cleaned-fits.xml"))


def package(aip):
    """Tars and zips the AIP, renames the file to include the unzipped size,
    and saves the resulting packaged AIP in the aips-to-ingest folder."""

    # Gets the operating system, since the tar and zip commands are different for Windows and Mac/Linux.
    operating_system = platform.system()

    # Makes a variable for the AIP folder name, which is reused a lot.
    aip_bag = f"{aip.id}_bag"

    # Gets the total size of the bag:
    # sum of the bag payload (data folder) from bag-info.txt and the size of the bag metadata files.
    # It saves time to use the bag payload instead of recalculating the size of a large data folder.
    bag_size = 0
    bag_info = open(os.path.join(aip_bag, "bag-info.txt"), "r")
    for line in bag_info:
        if line.startswith("Payload-Oxum"):
            payload = line.split()[1]
            bag_size += float(payload)
    for file in os.listdir(aip_bag):
        if file.endswith(".txt"):
            bag_size += os.path.getsize(os.path.join(aip_bag, file))
    bag_info.close()
    bag_size = int(bag_size)

    # Tars the file, using the command appropriate for the operating system.
    if operating_system == "Windows":
        # Does not print the progress to the terminal (stdout), which is a lot of text. [subprocess.DEVNULL]
        bag_path = os.path.join(aip.directory, aip_bag)
        tar_output = subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -ttar a "{aip_bag}.tar" "{bag_path}"',
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, shell=True)
        # If there is an error, saves the error to the log and does not complete the rest of the function for this AIP.
        # Cannot move it to an error folder because getting a permissions error.
        if not tar_output.stderr == b"":
            error_msg = tar_output.stderr.decode("utf-8")
            aip.log["Package"] = f"Could not tar. 7zip error: {error_msg}"
            aip.log["Complete"] = "Error during processing"
            log(aip.log)
            return
    else:
        subprocess.run(f'tar -cf "{aip_bag}.tar" "{aip_bag}"', shell=True)

    # Renames the file to include the size.
    os.replace(f"{aip_bag}.tar", f"{aip_bag}.{bag_size}.tar")

    # Updates the size in the AIP object so it can be used by the manifest() function later.
    aip.size = bag_size

    # If the AIP should be zipped (if the value of to_zip is true),
    # Zips (bz2) the tar file, using the command appropriate for the operating system.
    if aip.to_zip is True:
        aip_tar = f"{aip_bag}.{bag_size}.tar"
        if operating_system == "Windows":
            # Does not print the progress to the terminal (stdout), which is a lot of text.
            subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -tbzip2 a -aoa "{aip_tar}.bz2" "{aip_tar}"',
                           stdout=subprocess.DEVNULL, shell=True)
        else:
            subprocess.run(f'bzip2 "{aip_tar}"', shell=True)

        # Deletes the tar version. Just want the tarred and zipped version.
        # For Mac/Linux, the bzip2 command overwrites the tar file so this step is unnecessary.
        if operating_system == "Windows":
            os.remove(f"{aip_bag}.{bag_size}.tar")

        # Moves the tarred and zipped version to the aips-to-ingest folder.
        path = os.path.join("", "aips-to-ingest", f"{aip_bag}.{bag_size}.tar.bz2")
        os.replace(f"{aip_bag}.{bag_size}.tar.bz2", path)

    # If not zipping, moves the tarred version to the aips-to-ingest folder.
    else:
        path = os.path.join("", "aips-to-ingest", f"{aip_bag}.{bag_size}.tar")
        os.replace(f"{aip_bag}.{bag_size}.tar", path)

    # Updates log with success.
    aip.log["Package"] = "Successfully made package"


def structure_directory(aip):
    """Makes the AIP directory structure (objects and metadata folders within the AIP folder)
    and moves the digital objects into those folders. Anything not recognized as metadata is
    moved into the objects folder. If the digital objects are organized into folders, that
    directory structure is maintained within the objects folder. """

    # Makes the objects folder within the AIP folder, if it doesn't exist.
    # If it does, moves the AIP to an error folder so the original directory structure is not altered.
    try:
        os.mkdir(os.path.join(aip.id, "objects"))
        aip.log["ObjectsError"] = "Successfully created objects folder"
    except FileExistsError:
        aip.log["ObjectsError"] = "Objects folder already exists in original files"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        move_error("objects_folder_exists", aip.id)
        return

    # Makes the metadata folders within the AIP folder, if it doesn't exist.
    # If it does, moves the AIP to an error folder so the original directory structure is not altered.
    try:
        os.mkdir(os.path.join(aip.id, "metadata"))
        aip.log["MetadataError"] = "Successfully created metadata folder"
    except FileExistsError:
        aip.log["MetadataError"] = "Metadata folder already exists in original files"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        move_error("metadata_folder_exists", aip.id)
        return

    # Moves any metadata files to the metadata folder.
    # Departments or other details, in addition to the filenames, are used when possible.
    # The more specific the match, the less likely a file will be incorrectly identified as a metadata file.
    for item in os.listdir(aip.id):
        item_path = os.path.join(aip.id, item)
        metadata_path = os.path.join(aip.id, "metadata", item)
        # Deletion log, created by the AiP script when deleting temp files.
        if item.startswith(f"{aip.id}_files-deleted_"):
            os.replace(item_path, metadata_path)
        # Metadata file used by Emory with disk images.
        if aip.department == "emory" and item.startswith("EmoryMD"):
            os.replace(item_path, metadata_path)
        # Website metadata files from downloading WARCs from Archive-It
        web_metadata = ("_coll.csv", "_collscope.csv", "_crawldef.csv", "_crawljob.csv", "_seed.csv", "_seedscope.csv")
        if "-web-" in aip.id and item.endswith(web_metadata):
            os.replace(item_path, metadata_path)
        if aip.department == "magil" and item.endswith(web_metadata):
            os.replace(item_path, metadata_path)

    # Moves all remaining files and folders to the objects folder.
    # The first level within the AIPs folder is now just the metadata folder and objects folder.
    for item in os.listdir(aip.id):
        if item in ("metadata", "objects"):
            continue
        os.replace(os.path.join(aip.id, item), os.path.join(aip.id, "objects", item))


def validate_bag(aip):
    """Validates the AIP's bag.
    If it is not valid, moves the AIP to an error folder and saves the error output to that error folder."""

    new_bag = bagit.Bag(f"{aip.id}_bag")
    try:
        new_bag.validate()
        aip.log["BagValid"] = f"Bag valid on {datetime.datetime.now()}"
    except bagit.BagValidationError as errors:
        aip.log["BagValid"] = "Bag not valid (see log in bag_not_valid error folder)"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        move_error("bag_not_valid", f"{aip.id}_bag")
        # Error log is formatted to be easier to read (one error per line) if error information is in details.
        # Otherwise, the entire error output is saved to the log.
        log_path = os.path.join("", "errors", "bag_not_valid", f"{aip.id}_bag_validation.txt")
        with open(log_path, "w") as log_path:
            if errors.details:
                for error_type in errors.details:
                    log_path.write(str(error_type) + "\n")
            else:
                log_path.write(str(errors))


def validate_preservation_xml(aip):
    """Verifies that the preservation.xml file meets the metadata requirements for the
    UGA Libraries' digital preservation system (ARCHive)."""

    # Uses xmllint and a XSD file to validate the preservation.xml.
    input_file = os.path.join(aip.id, "metadata", f"{aip.id}_preservation.xml")
    stylesheet = os.path.join(c.STYLESHEETS, "preservation.xsd")
    xmllint_output = subprocess.run(f'xmllint --noout -schema "{stylesheet}" "{input_file}"',
                                    stderr=subprocess.PIPE, shell=True)

    # Converts the xmllint output to a string for easier tests for possible error types.
    validation_result = xmllint_output.stderr.decode("utf-8")

    # If the preservation.xml file was not made in the expected location, moves the AIP to an error folder.
    # If it was made, updates the log with the success.
    if "failed to load" in validation_result:
        aip.log["PresXML"] = f"Preservation.xml was not created. xmllint error: {validation_result}"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        move_error("preservationxml_not_found", aip.id)
        return
    else:
        aip.log["PresXML"] = "Successfully created preservation.xml"

    # If the preservation.xml does not meet the requirements, moves the AIP to an error folder.
    # The validation output is saved to a file in the error folder for review.
    # If it valid, updates the log with the success.
    if "fails to validate" in validation_result:
        aip.log["PresValid"] = "Preservation.xml is not valid (see log in error folder)"
        aip.log["Complete"] = "Error during processing"
        log(aip.log)
        move_error("preservationxml_not_valid", aip.id)
        log_path = os.path.join("", "errors", "preservationxml_not_valid", f"{aip.id}_presxml_validation.txt")
        with open(log_path, "w") as validation_log:
            for line in validation_result.split("\r"):
                validation_log.write(line + "\n")
        return
    else:
        aip.log["PresValid"] = f"Preservation.xml valid on {datetime.datetime.now()}"