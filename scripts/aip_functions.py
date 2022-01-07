""" Functions used to make AIPs from folders of digital objects that are ready for ingest into the
UGA Libraries' digital preservation system (ARCHive). These are utilized by multiple scripts that
create AIPs of different types."""

import csv
import datetime
import os
import platform
import shutil
import subprocess
import xml.etree.ElementTree as ET
import bagit

# Constants with the absolute file paths for programs and files used by the functions.
import configuration as c


def log(log_path, log_item):
    """Saves information about an error or event to its own line in a text file."""

    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f'{log_item}\n')


def move_error(error_name, item):
    """Moves the AIP folder to an error folder, named with the error type, so the rest of the
    workflow steps are not completed on it. Makes the error folder if it does not already exist
    prior to moving the AIP folder. """

    if not os.path.exists(f'../errors/{error_name}'):
        os.makedirs(f'../errors/{error_name}')
    os.replace(item, f'../errors/{error_name}/{item}')


def check_paths():
    """Verifies all the paths from the configuration file are valid.
    Returns a list of paths with errors or "no errors".
    This avoids wasting processing time by doing earlier steps before the path error is encountered."""

    errors = []
    for path in (c.FITS, c.SAXON, c.MD5DEEP, c.STYLESHEETS):
        if not os.path.exists(path):
            errors.append(path)

    if len(errors) == 0:
        return "no errors"
    else:
        return errors


def make_output_directories():
    """Makes the directories used to store script outputs, if they don't already exist,
    in the parent folder of the AIPs directory."""

    directories = ['aips-to-ingest', 'fits-xml', 'preservation-xml']

    for directory in directories:
        if not os.path.exists(f'../{directory}'):
            os.mkdir(f'../{directory}')


def delete_temp(aip_id, log_path):
    """Deletes temporary files of various types from anywhere within the AIP folder because they cause errors later
    in the workflow, especially with bag validation. Creates a log of the deleted files as a record of actions taken
    on the AIP during processing. This is especially important if there are large files that result in a noticeable
    change in size after making the AIP. """

    # List of files to be deleted where the filename can be matched in its entirely.
    delete = ['.DS_Store', '._.DS_Store', 'Thumbs.db']

    # List of files that were deleted, to save to a log if desired.
    deleted_files = []

    # Checks all files at any level in the AIP folder and deletes them if they match one of the
    # criteria for being temporary. If a log is desired, adds the path of the deleted file to a list.
    for root, directories, files in os.walk(aip_id):
        for item in files:
            if item in delete or item.endswith('.tmp') or item.startswith('.'):
                deleted_files.append([os.path.join(root, item), item])
                os.remove(os.path.join(root, item))

    # Creates the log in the AIP folder if any files were deleted.
    # The log contains the path and filename of every deleted file.
    if len(deleted_files) > 0:
        with open(f"{aip_id}/Files_Deleted_{datetime.datetime.today().date()}_del.csv", "w", newline="") as deleted_log:
            deleted_log_writer = csv.writer(deleted_log)
            deleted_log_writer.writerow(["Path", "File Name"])
            for file_data in deleted_files:
                deleted_log_writer.writerow(file_data)
        log(log_path, "Temporary files were deleted. See the log in the metadata folder for details.")


def structure_directory(aip_id, department, log_path):
    """Makes the AIP directory structure (objects and metadata folders within the AIP folder)
    and moves the digital objects into those folders. Anything not recognized as metadata is
    moved into the objects folder. If the digital objects are organized into folders, that
    directory structure is maintained within the objects folder. """

    # Makes the objects and metadata folders within the AIP folder, if they don't exist.
    # Otherwise, moves the AIP to an error folder so the directory structure is not altered.
    try:
        os.mkdir(f'{aip_id}/objects')
    except FileExistsError:
        log(log_path, "Stop processing. Objects folder already exists.")
        move_error("objects_folder_exists", aip_id)
        return
    try:
        os.mkdir(f"{aip_id}/metadata")
    except FileExistsError:
        log(log_path, "Stop processing. Metadata folder already exists.")
        move_error("metadata_folder_exists", aip_id)
        return

    # Moves any metadata files, identified by their file names and department if not all use it, to the metadata folder.
    for item in os.listdir(aip_id):
        if item.startswith("Files_Deleted_"):
            os.replace(f"{aip_id}/{item}", f"{aip_id}/metadata/{item}")
        if department == "emory" and item.startswith("EmoryMD"):
            os.replace(f"{aip_id}/{item}", f"{aip_id}/metadata/{item}")

    # Moves all remaining files and folders to the objects folder.
    # The first level within the AIPs folder is now just the metadata folder and objects folder.
    for item in os.listdir(aip_id):
        if item in ("metadata", "objects"):
            continue
        os.replace(f"{aip_id}/{item}", f"{aip_id}/objects/{item}")


def extract_metadata(aip_id, aip_directory, log_path):
    """Extracts technical metadata from the files in the objects folder using FITS and
    creates a single XML file that combines the FITS output for every file in the AIP. """

    # Runs FITS on the files in the AIP's objects folder and saves the output to it's metadata folder.
    # The FITS output is named with the original file name. If there is more than one file anywhere
    # within the objects folder with the same name, FITS adds a number to the duplicates, for example:
    # file.ext.fits.xml, file.ext-1.fits.xml, file.ext-2.fits.xml
    fits_output = subprocess.run(
        f'"{c.FITS}" -r -i "{aip_directory}/{aip_id}/objects" -o "{aip_directory}/{aip_id}/metadata"',
        shell=True, stderr=subprocess.PIPE)

    # If there were any tool error messages from FITS, saves those to a log in the AIP's metadata folder.
    # Processing on the AIP continues, since typically other tools still work.
    if fits_output.stderr:
        with open(f"{aip_directory}/{aip_id}/metadata/{aip_id}_fits-tool-errors_fitserr.txt", "w") as fits_errors:
            fits_errors.write(fits_output.stderr.decode('utf-8'))
    log(log_path, "At least one FITs tool had an error with this AIP. See the log in the metadata folder for details.")

    # Renames the FITS output to the UGA Libraries' metadata naming convention (filename_fits.xml).
    for item in os.listdir(f'{aip_id}/metadata'):
        if item.endswith('.fits.xml'):
            new_name = item.replace('.fits', '_fits')
            os.rename(f'{aip_id}/metadata/{item}', f'{aip_id}/metadata/{new_name}')

    # The rest of this function copies the FITS output into a single XML file.

    # Makes a new XML object with the root element named combined-fits.
    combo_tree = ET.ElementTree(ET.Element('combined-fits'))
    combo_root = combo_tree.getroot()

    # Gets each of the FITS documents in the AIP's metadata folder.
    for doc in os.listdir(f'{aip_id}/metadata'):
        if doc.endswith('_fits.xml'):

            # Makes Python aware of the FITS namespace.
            ET.register_namespace('', "http://hul.harvard.edu/ois/xml/ns/fits/fits_output")

            # Gets the FITS element and its children and makes it a child of the root, combined-fits.
            try:
                tree = ET.parse(f'{aip_id}/metadata/{doc}')
                root = tree.getroot()
                combo_root.append(root)
            # Errors: the file is empty, is not XML, has invalid XML, or has the wrong namespace.
            # Moves the AIP to an error folder and does not execute the rest of this function.
            except ET.ParseError:
                log(log_path, 'Stop processing. Error combining FITS into one XML file.')
                move_error('combining_fits', aip_id)
                return

    # Saves the combined-fits XML to a file named aip-id_combined-fits.xml in the AIP's metadata folder.
    combo_tree.write(f'{aip_id}/metadata/{aip_id}_combined-fits.xml', xml_declaration=True, encoding='UTF-8')


def make_preservationxml(aip_id, collection_id, aip_title, department, workflow, log_path):
    """Creates PREMIS and Dublin Core metadata from the combined FITS XML and saves it as a file
    named preservation.xml that meets the metadata requirements for the UGA Libraries' digital
    preservation system (ARCHive)."""

    # Makes a simplified version of the combined fits XML so the XML is easier to aggregate.
    # Saves the file in the AIP's metadata folder. It is deleted at the end of the function.
    combined_fits = f'{aip_id}/metadata/{aip_id}_combined-fits.xml'
    cleanup_stylesheet = f'{c.STYLESHEETS}/fits-cleanup.xsl'
    cleaned_fits = f'{aip_id}/metadata/{aip_id}_cleaned-fits.xml'
    subprocess.run(
        f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{combined_fits}" -xsl:"{cleanup_stylesheet}" -o:"{cleaned_fits}"',
        shell=True)

    # Makes the preservation.xml file using a stylesheet and saves it to the AIP's metadata folder.
    stylesheet = f'{c.STYLESHEETS}/fits-to-preservation.xsl'
    preservation_xml = f'{aip_id}/metadata/{aip_id}_preservation.xml'
    arguments = f'collection-id="{collection_id}" aip-id="{aip_id}" aip-title="{aip_title}" department="{department}" workflow="{workflow}" ns={c.NAMESPACE}'
    subprocess.run(
        f'java -cp "{c.SAXON}" net.sf.saxon.Transform -s:"{cleaned_fits}" -xsl:"{stylesheet}" -o:"{preservation_xml}" {arguments}',
        shell=True)

    # Validates the preservation.xml file against the requirements of ARCHive.
    # If it is not valid, saves the validation error to the log, moves the AIP to an error folder,
    # and does not execute the rest of this function.
    validation = subprocess.run(f'xmllint --noout -schema "{c.STYLESHEETS}/preservation.xsd" "{preservation_xml}"',
                                stderr=subprocess.PIPE, shell=True)
    validation_result = str(validation.stderr)

    # This error happens if the preservation.xml file was not made in the expected location.
    if 'failed to load' in validation_result:
        log(log_path, f'Stop processing. Unable to find the preservation.xml file. Error:\n{validation_result}')
        move_error('preservationxml_not_found', aip_id)
        return

    # This error happens if the preservation.xml file does not meet the Libraries' requirements.
    if 'fails to validate' in validation_result:
        log(log_path, f'Stop processing. The preservation.xml file is not valid. Error:\n{validation_result}')
        move_error('preservationxml_not_valid', aip_id)
        return

    # Copies the preservation.xml file to the preservation-xml folder for staff reference.
    shutil.copy2(f'{aip_id}/metadata/{aip_id}_preservation.xml', '../preservation-xml')

    # Moves the combined-fits.xml file to the fits-xml folder for staff reference.
    os.replace(f'{aip_id}/metadata/{aip_id}_combined-fits.xml', f'../fits-xml/{aip_id}_combined-fits.xml')

    # Deletes the cleaned-fits.xml file because it is a temporary file.
    os.remove(f'{aip_id}/metadata/{aip_id}_cleaned-fits.xml')


def bag(aip_id, log_path):
    """Bags and validates the AIP. Adds _bag to the AIP folder name."""

    # Bags the AIP folder in place with md5 and sha256 checksums for extra security.
    bagit.make_bag(aip_id, checksums=['md5', 'sha256'])

    # Renames the AIP folder to add _bag to the end of the folder name.
    new_aip_name = f'{aip_id}_bag'
    os.replace(aip_id, new_aip_name)

    # Validates the bag.
    # If it is not valid, saves the validation errors to the log, moves the AIP to an error folder.
    new_bag = bagit.Bag(new_aip_name)
    try:
        new_bag.validate()
    except bagit.BagValidationError as errors:
        log(log_path, f'Stop processing. Bag is not valid: \n{errors}')
        move_error('bag_invalid', f'{aip_id}_bag')


def package_and_manifest(aip_id, aips_directory, department, to_zip):
    """Tars and zips the AIP. Saves the resulting packaged AIP in the aips-to-ingest folder.
    Also uses md5 deep to calculate the MD5 for the AIP and adds it to the manifest for that department
    in the aips-to-ingest folder. Each department has a separate manifest so AIPs for multiple departments
    may be created simultaneously."""

    # Get operating system, since the tar and zip commands are different for Windows and Mac/Linux.
    operating_system = platform.system()

    # Makes a variable for the AIP folder name, which is reused a lot.
    aip = f'{aip_id}_bag'

    # Gets the total size of the bag:
    # sum of the bag payload (data folder) from bag-info.txt and the size of the bag metadata files.
    # It saves time to use the bag payload instead of recalculating the size of a large data folder.
    bag_size = 0
    bag_info = open(f"{aip}/bag-info.txt", "r")
    for line in bag_info:
        if line.startswith("Payload-Oxum"):
            payload = line.split()[1]
            bag_size += float(payload)
    for file in os.listdir(aip):
        if file.endswith('.txt'):
            bag_size += os.path.getsize(f"{aip}/{file}")
    bag_size = int(bag_size)

    # Tars the file, using the command appropriate for the operating system.
    if operating_system == "Windows":
        # Does not print the progress to the terminal (stdout), which is a lot of text.
        subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -ttar a "{aip}.tar" "{aips_directory}/{aip}"',
                       stdout=subprocess.DEVNULL, shell=True)
    else:
        subprocess.run(f'tar -cf "{aip}.tar" "{aip}"', shell=True)

    # Renames the file to include the size.
    os.replace(f'{aip}.tar', f'{aip}.{bag_size}.tar')

    # If the AIP should be zipped (if the value of to_zip is true),
    # Zips (bz2) the tar file, using the command appropriate for the operating system.
    if to_zip is True:
        if operating_system == "Windows":
            # Does not print the progress to the terminal (stdout), which is a lot of text.
            subprocess.run(
                f'"C:/Program Files/7-Zip/7z.exe" -tbzip2 a -aoa "{aip}.{bag_size}.tar.bz2" "{aip}.{bag_size}.tar"',
                stdout=subprocess.DEVNULL, shell=True)
        else:
            subprocess.run(f'bzip2 "{aip}.{bag_size}.tar"', shell=True)

        # Deletes the tar version. Just want the tarred and zipped version.
        # For Mac/Linux, the bzip2 command overwrites the tar file so this step is unnecessary.
        if operating_system == "Windows":
            os.remove(f'{aip}.{bag_size}.tar')

        # Calculates the MD5 of the tarred and zipped AIP and adds it to the manifest in the aips-to-ingest folder.
        md5 = subprocess.run(f'"{c.MD5DEEP}" -br "{aip}.{bag_size}.tar.bz2"', stdout=subprocess.PIPE, shell=True)
        manifest_path = os.path.join(f'../aips-to-ingest', f"manifest_{department}.txt")
        with open(manifest_path, 'a', encoding='utf-8') as manifest_file:
            manifest_file.write(md5.stdout.decode("UTF-8").rstrip("\n"))

        # Moves the tarred and zipped version to the aips-to-ingest folder.
        path = os.path.join(f'../aips-to-ingest', f"{aip}.{bag_size}.tar.bz2")
        os.replace(f"{aip}.{bag_size}.tar.bz2", path)

    # If not zipping.
    else:
        # Calculates the MD5 of the tarred and zipped AIP and adds it to the manifest in the aips-to-ingest folder.
        md5 = subprocess.run(f'"{c.MD5DEEP}" -br "{aip}.{bag_size}.tar"', stdout=subprocess.PIPE, shell=True)
        manifest_path = os.path.join(f'../aips-to-ingest', f"manifest_{department}.txt")
        with open(manifest_path, 'a', encoding='utf-8') as manifest_file:
            manifest_file.write(md5.stdout.decode("UTF-8").rstrip("\n"))

        # Moves the tarred version to the aips-to-ingest folder.
        path = os.path.join(f'../aips-to-ingest', f"{aip}.{bag_size}.tar")
        os.replace(f"{aip}.{bag_size}.tar", path)
