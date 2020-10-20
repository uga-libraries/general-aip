""" Functions used to make AIPs from folders of digital objects that are then ready for ingest into the
UGA Libraries' digital preservation system (ARCHive). These are utilized by multiple scripts that create AIPs of
different types."""

import bagit
import os
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


def delete_temp(aip_id, log_path=False):
    """Deletes temporary files of various types from anywhere within the AIP folder because they cause errors later in
    the workflow, especially with bag validation."""

    # List of files to be deleted where the filename can be matched in its entirely.
    delete = ['.DS_Store', '._.DS_Store', 'Thumbs.db']

    # Checks all files at any level in the AIP folder and deletes them if they match one of the criteria for
    # being temporary. If a log path is provided, adds the file name to the log.
    for root, directories, files in os.walk(aip_id):
        for item in files:
            if item in delete or item.endswith('.tmp') or item.startswith('.'):
                if log_path:
                    log(log_path, f'Deleted temporary file: {root}/{item}')
                os.remove(f'{root}/{item}')


def structure_directory(aip_id, log_path):
    """Makes the AIP directory structure (objects and metadata folder within the AIP folder) and moves the digital
    objects into the objects folder. If the digital objects are organized into folders, that directory structure is
    maintained within the objects folder."""

    # Makes the objects folder within the AIP folder, if it doesn't exist. If it does exist, moves the AIP to an
    # error folder and does not execute the rest of this function so the original directory structure is not altered.
    try:
        os.mkdir(f'{aip_id}/objects')
    except FileExistsError:
        log(log_path, 'Stop processing. Objects folder already exists.')
        move_error('objects_folder_exists', aip_id)
        return

    # Moves the contents of the AIP folder into the objects folder.
    for item in os.listdir(aip_id):
        if item == 'objects':
            continue
        os.replace(f'{aip_id}/{item}', f'{aip_id}/objects/{item}')

    # Makes the metadata folder within the AIP folder, if it doesn't exist. If it does exist, moves the AIP to an
    # error folder. If this happens, there was an error in the previous step when everything should have been moved
    # to the objects folder.
    try:
        os.mkdir(f'{aip_id}/metadata')
    except FileExistsError:
        log(log_path, 'Stop processing. Metadata folder already exists.')
        move_error('metadata_folder_exists', aip_id)


def extract_metadata(aip_id, aip_directory, log_path):
    """Extracts technical metadata from the files in the objects folder using FITS and creates a single XML file that
    combines the FITS output for every file in the AIP. """

    # Runs FITS on every file in the AIP's objects folder and saves the output to the AIP's metadata folder.
    subprocess.run(f'"{c.fits}" -r -i "{aip_directory}/{aip_id}/objects" -o "{aip_directory}/{aip_id}/metadata"', shell=True)

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

    # Updates the department variable from the code used in the AIP id to the group name in ARCHive. The regular
    # expression used to extract the department code from the AIP id ensures it is either harg or rbrl.
    if department == 'harg':
        department = 'hargrett'
    else:
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


def package(aip_id, log_path):
    """Bags, tars, and zips each AIP."""

    # Bags the AIP folder in place. Both md5 and sha256 checksums are generated to guard against tampering.
    bagit.make_bag(aip_id, checksums=['md5', 'sha256'])

    # Renames the AIP folder to add _bag to the end of the folder name.
    new_aip_name = f'{aip_id}_bag'
    os.replace(aip_id, new_aip_name)

    # Validates the bag. If it is not valid, saves the validation errors to the log, moves the AIP to an error folder,
    # and does not execute the rest of this function.
    new_bag = bagit.Bag(new_aip_name)
    try:
        new_bag.validate()
    except bagit.BagValidationError as e:
        log(log_path, f'Stop processing. Bag is not valid: \n{e}')
        move_error('bag_invalid', f'{aip_id}_bag')
        return

    # Tars and zips the AIP using a perl script and saves the packaged AIP in the aips-to-ingest folder.
    # The script also adds the uncompressed file size to the file name.
    subprocess.run(f'perl "{c.prepare_bag_script}" "{aip_id}_bag" "../aips-to-ingest"', shell=True)

    # When the script for Windows is used, it saves both the tar version and tar.bzip2 version to the aips-to-ingest
    # folder. Deletes the tar only version.
    for file in os.listdir('../aips-to-ingest'):
        if file.endswith('.tar'):
            os.remove(f'../aips-to-ingest/{file}')


def make_manifest():
    """Makes a MD5 manifest of all AIPs in this batch using md5deep. The manifest is named department_manifest.txt
    and saved in the aips-to-ingest folder. If AIPs for multiple departments are present in the same batch,
    a separate manifest is made for each department. The manifest has one line per AIP, formatted md5<tab>filename"""

    # Changes the current directory to the location of the packaged AIPs.
    os.chdir('../aips-to-ingest')

    # Uses md5deep to calculate the MD5s for files with the specified department prefix and saves them to the manifest.
    # Tests if there are any files with that prefix before making the manifest so it does not make an empty manifest.
    if any(file.startswith('harg') for file in os.listdir('.')):
        subprocess.run(f'{c.md5deep} -br harg* > manifest_hargrett.txt', shell=True)

    if any(file.startswith('rbrl') for file in os.listdir('.')):
        subprocess.run(f'{c.md5deep} -br rbrl* > manifest_russell.txt', shell=True)
