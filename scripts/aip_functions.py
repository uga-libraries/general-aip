""" Functions used to make AIPs from folders of digital objects that are then ready for ingest into the
UGA Libraries' digital preservation system (ARCHive). These are utilized by multiple scripts that create AIPs of
different types."""

import bagit
import datetime
import os
import platform
import shutil
import subprocess
import xml.etree.ElementTree as ET

# Constants with the absolute file paths for programs and files used by the functions.
import configuration as c


def log(log_path, log_item):
    """Saves information about an error or event to its own line in a text file."""

    with open(log_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f'{log_item}\n')


def move_error(error_name, item):
    """Moves the AIP folder to an error folder, named with the error type, so the rest of the workflow steps are not
    completed on it. Makes the error folder if it does not already exist prior to moving the AIP folder. """

    if not os.path.exists(f'../errors/{error_name}'):
        os.makedirs(f'../errors/{error_name}')
    os.replace(item, f'../errors/{error_name}/{item}')


def make_output_directories():
    """Makes the directories used to store script outputs, if they don't already exist, in the parent folder of the AIPs
    directory."""

    directories = ['aips-to-ingest', 'fits-xml', 'preservation-xml']

    for directory in directories:
        if not os.path.exists(f'../{directory}'):
            os.mkdir(f'../{directory}')


def delete_temp(aip_id, deletion_log=False):
    """Deletes temporary files of various types from anywhere within the AIP folder because they cause errors later in
    the workflow, especially with bag validation."""

    # List of files to be deleted where the filename can be matched in its entirely.
    delete = ['.DS_Store', '._.DS_Store', 'Thumbs.db']

    # List of files that were deleted, to save to a log if desired.
    deleted_files = []

    # Checks all files at any level in the AIP folder and deletes them if they match one of the criteria for
    # being temporary. If a log is desired, adds the path of the deleted file to a list.
    for root, directories, files in os.walk(aip_id):
        for item in files:
            if item in delete or item.endswith('.tmp') or item.startswith('.'):
                if deletion_log:
                    deleted_files.append(os.path.join(root, item))
                os.remove(os.path.join(root, item))

    # Creates the log in the AIP folder if a log is desired and any files were deleted.
    # The log contains the path of every deleted file.
    if len(deleted_files) > 0:
        deleted_log = open(f"{aip_id}/Temporary_Files_Deleted_{datetime.datetime.today().date()}_del.txt", "w")
        for file in deleted_files:
            deleted_log.write(file + "\n")


def structure_directory(aip_id, log_path):
    """Makes the AIP directory structure (objects and metadata folders within the AIP folder) and moves the digital
    objects into those folders. Anything not recognized as metadata is moved into the objects folder. If the digital
    objects are organized into folders, that directory structure is maintained within the objects folder. """

    # Makes the objects and metadata folders within the AIP folder, if they don't exist.
    # If they do exist, moves the AIP to an error folder so the original directory structure is not altered.
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

    # Moves any metadata files, identified by their file names, to the metadata folder.
    for item in os.listdir(aip_id):
        if item.startswith("Temporary_Files_Deleted_") or item.startswith("EmoryMD"):
            os.replace(f"{aip_id}/{item}", f"{aip_id}/metadata/{item}")

    # Moves all remaining files and folders to the objects folder.
    # The first level within the AIPs folder is now just the metadata folder and objects folder.
    for item in os.listdir(aip_id):
        if item == "metadata" or item == "objects":
            continue
        os.replace(f"{aip_id}/{item}", f"{aip_id}/objects/{item}")


def extract_metadata(aip_id, aip_directory, log_path):
    """Extracts technical metadata from the files in the objects folder using FITS and creates a single XML file that
    combines the FITS output for every file in the AIP. """

    # Runs FITS on every file in the AIP's objects folder and saves the output to the AIP's metadata folder.
    # FITS output is named with the original file name. If there is more than one file anywhere within the 
    # objects folder with the same name, FITS automatically adds a number to the duplicates, for example: 
    # file.ext.fits.xml, file.ext-1.fits.xml, file.ext-2.fits.xml 
    
    # TODO: catch error if FITS does not run.
    #  In terminal, prints Error: Could not find or load main class edu.harvard.hul.ois.fits.Fits.
    #  Happened when running the script with an AIPs directory that is on an external hard drive.
    #  The function still makes combined-fits.xml, which just has the xml declaration and <combined-fits/>
    #  The error will be caught when preservation.xml is not valid.
    subprocess.run(f'"{c.fits}" -r -i "{aip_directory}/{aip_id}/objects" -o "{aip_directory}/{aip_id}/metadata"',
                   shell=True)

    # Renames the FITS output according to the UGA Libraries' metadata naming convention (filename_fits.xml).
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

            # Gets the FITS element (and all its children) and makes it a child of the XML object's root, combined-fits.
            # If there is an error, moves the AIP to an error folder and does not execute the rest of this function.
            try:
                tree = ET.parse(f'{aip_id}/metadata/{doc}')
                root = tree.getroot()
                combo_root.append(root)
            # This error catches if the file is empty, is not XML, has invalid XML, or has the wrong namespace.
            except ET.ParseError:
                log(log_path, 'Stop processing. Error combining FITS into one XML file.')
                move_error('combining_fits', aip_id)
                return

    # Saves the combined-fits XML object to a file named aip-id_combined-fits.xml in the AIP's metadata folder.
    combo_tree.write(f'{aip_id}/metadata/{aip_id}_combined-fits.xml', xml_declaration=True, encoding='UTF-8')


def make_preservationxml(aip_id, aip_title, department, workflow, log_path):
    """Creates PREMIS and Dublin Core metadata from the combined FITS XML and saves it as a file named preservation.xml
    that meets the metadata requirements for the UGA Libraries' digital preservation system (ARCHive)."""

    # Makes a simplified (cleaned) version of the combined fits XML with a stylesheet so the XML is easier to aggregate.
    # Temporarily saves the file in the AIP's metadata folder. It is deleted at the end of the function.
    combined_fits = f'{aip_id}/metadata/{aip_id}_combined-fits.xml'
    cleanup_stylesheet = f'{c.stylesheets}/fits-cleanup.xsl'
    cleaned_fits = f'{aip_id}/metadata/{aip_id}_cleaned-fits.xml'
    subprocess.run(
        f'java -cp {c.saxon} net.sf.saxon.Transform -s:"{combined_fits}" -xsl:"{cleanup_stylesheet}" -o:"{cleaned_fits}"',
        shell=True)

    # Counts the number of files in the objects folder, since a different stylesheet is used for AIPs with one file.
    file_count = 0
    for root, directories, files in os.walk(f'{aip_id}/objects'):
        file_count += len(files)

    # Selects the correct stylesheet for if the AIP has one file or multiple files. If there is not at least 1 file,
    # moves the AIP to an error folder and does not execute the rest of this function.
    if file_count == 1:
        stylesheet = f'{c.stylesheets}/fits-to-preservation_singlefile.xsl'
    elif file_count > 1:
        stylesheet = f'{c.stylesheets}/fits-to-preservation_multifile.xsl'
    else:
        log(log_path, 'Stop processing. There are no objects in this AIP.')
        move_error('no_files', aip_id)
        return

    # Updates the department variable from the code used in the AIP id to the group name in ARCHive, if different.
    if department == 'harg':
        department = 'hargrett'
    elif department == 'rbrl':
        department = 'russell'

    # Makes the preservation.xml file using a stylesheet and saves it to the AIP's metadata folder.
    preservation_xml = f'{aip_id}/metadata/{aip_id}_preservation.xml'
    subprocess.run(
        f'java -cp {c.saxon} net.sf.saxon.Transform -s:"{cleaned_fits}" -xsl:"{stylesheet}" -o:"{preservation_xml}" '
        f'aip-id="{aip_id}" aip-title="{aip_title}" department="{department}" workflow="{workflow}"',
        shell=True)

    # Validates the preservation.xml file against the requirements of the UGA Libraries' digital preservation system
    # (ARCHive). If it is not valid, saves the validation error to the log, moves the AIP to an error folder,
    # and does not execute the rest of this function.
    validation = subprocess.run(f'xmllint --noout -schema "{c.stylesheets}/preservation.xsd" "{preservation_xml}"',
                                stderr=subprocess.PIPE, shell=True)
    validation_result = str(validation.stderr)

    # This error happens if the preservation.xml file was not made or is not in the expected location.
    if 'failed to load' in validation_result:
        log(log_path, f'Stop processing. Unable to find the preservation.xml file. Error:\n{validation_result}')
        move_error('preservationxml_not_found', aip_id)
        return

    # This error happens if the preservation.xml file does not meet the Libraries' requirements.
    elif 'fails to validate' in validation_result:
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

    # Bags the AIP folder in place. Both md5 and sha256 checksums are generated to guard against tampering.
    bagit.make_bag(aip_id, checksums=['md5', 'sha256'])

    # Renames the AIP folder to add _bag to the end of the folder name.
    new_aip_name = f'{aip_id}_bag'
    os.replace(aip_id, new_aip_name)

    # Validates the bag. If it is not valid, saves the validation errors to the log, moves the AIP to an error folder.
    new_bag = bagit.Bag(new_aip_name)
    try:
        new_bag.validate()
    except bagit.BagValidationError as e:
        log(log_path, f'Stop processing. Bag is not valid: \n{e}')
        move_error('bag_invalid', f'{aip_id}_bag')


def package(aip_id, aips_directory):
    """Tars and zips the AIP. Saves the resulting packaged AIP in the aips-to-ingest folder."""

    # Get operating system, since the tar and zip commands are different for Windows and Mac/Linux.
    operating_system = platform.system()

    # Makes a variable for the AIP folder name, which is reused a lot.
    aip = f'{aip_id}_bag'

    # Gets the total size of the bag: sum of the bag payload (data folder) from bag-info.txt and bag metadata files.
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
        subprocess.run(f'7z -ttar a "{aip}.tar" "{aips_directory}/{aip}"', stdout=subprocess.DEVNULL, shell=True)
    else:
        subprocess.run(f'tar -cf "{aip}.tar" "{aip}"', shell=True)

    # Renames the file to include the size.
    os.replace(f'{aip}.tar', f'{aip}.{bag_size}.tar')

    # Zips (bz2) the tar file, using the command appropriate for the operating system.
    if operating_system == "Windows":
        # Does not print the progress to the terminal (stdout), which is a lot of text.
        subprocess.run(f'7z -tbzip2 a -aoa "{aip}.{bag_size}.tar.bz2" "{aip}.{bag_size}.tar"',
                       stdout=subprocess.DEVNULL, shell=True)
    else:
        subprocess.run(f'bzip2 "{aip}.{bag_size}.tar"', shell=True)

    # Deletes the tar version. Just want the tarred and zipped version.
    # For Mac/Linux, the bzip2 command overwrites the tar file so this step is unnecessary.
    if operating_system == "Windows":
        os.remove(f'{aip}.{bag_size}.tar')

    # Moves the tarred and zipped version to the aips-to-ingest folder.
    path = os.path.join(f'../aips-to-ingest', f"{aip}.{bag_size}.tar.bz2")
    os.replace(f"{aip}.{bag_size}.tar.bz2", path)


def make_manifest():
    """Makes a MD5 manifest of all AIPs in this batch using md5deep. The manifest is named department_manifest.txt
    and saved in the aips-to-ingest folder. If AIPs for multiple departments are present in the same batch,
    a separate manifest is made for each department. The manifest has one line per AIP, formatted md5<tab>filename"""

    # Changes the current directory to the location of the packaged AIPs.
    os.chdir('../aips-to-ingest')

    # Uses md5deep to calculate the MD5s for files with the specified prefix and saves them to the manifest.
    # Tests if there are any files with that prefix before making the manifest so it does not make an empty manifest.
    if any(file.startswith('harg') for file in os.listdir('.')):
        subprocess.run(f'{c.md5deep} -br harg* > manifest_hargrett.txt', shell=True)

    if any(file.startswith('rbrl') for file in os.listdir('.')):
        subprocess.run(f'{c.md5deep} -br rbrl* > manifest_russell.txt', shell=True)

    if any(file.startswith('emory') for file in os.listdir('.')):
        subprocess.run(f'{c.md5deep} -br emory* > manifest.txt', shell=True)
