"""Creates AIPs from folders of digital objects that are ready for ingest into our digital preservation system (ARCHive)

The AIPs may contain one or multiple files of any format.
The script works with Hargrett and Russell library born-digital IDs,
Hargrett, MAGIL and Russell web IDs, and Emory disk image IDs.

Parameters:
    aips_directory : required,  folder that contains the folders to be made into AIPs
    no-zip : optional, use if AIP should only be tarred and not zipped

Returns:
    The aips_directory folder with the AIP bags, which are complete AIPs except for zipping
    aip_log.csv with the status of each script step
    aips-to-ingest folder with completed AIPs and a manifest
    errors folder (if there were errors), with folders for each error encountered containing the AIP folders
    fits-xml folder with combined FITS XML for each AIP, for reference (FITS XML for each file is in the AIP)
    preservation-xml folder with preservation.xml for each AIP, for reference (a copy is in the AIP)
"""

import csv
import os
import sys
import aip_functions as a

# Verifies the script arguments are correct and calculates the associated variables.
# If there are errors, ends the script.
AIPS_DIRECTORY, ZIP, aip_metadata_csv, argument_errors = a.check_arguments(sys.argv)
if len(argument_errors) > 0:
    print('\nProblems detected with the provided script arguments:')
    for error in argument_errors:
        print("   * " + error)
    print('\nScript usage: python "path/general_aip.py" "path/aips-directory" [no-zip]')
    print("Correct the script arguments and run the script again.")
    sys.exit()

# Makes the current directory the AIPs directory
os.chdir(AIPS_DIRECTORY)

# Verifies all the variables from the configuration file are present and all the paths are valid.
# If not, ends the script.
configuration_errors = a.check_configuration()
if len(configuration_errors) > 0:
    print('\nProblems detected with configuration.py:')
    for error in configuration_errors:
        print("   * " + error)
    print('\nCorrect the configuration file and run the script again. Use configuration_template.py as a model.')
    sys.exit()

# Reads the CSV with the AIP metadata.
open_metadata = open(aip_metadata_csv)
read_metadata = csv.reader(open_metadata)

# Verifies the metadata header row has the expected values, departments are all ARCHive groups, and the folders match
# what is in the AIPs directory. If there are an errors, ends the script.
metadata_errors = a.check_metadata_csv(read_metadata)
if len(metadata_errors) > 0:
    print('\nProblems detected with metadata.csv:')
    for error in metadata_errors:
        print("   * " + error)
    print('\nCorrect the metadata.csv and run the script again.')
    sys.exit()

# If there isn't already a log from running this script on a previous batch,
# starts a log for saving information about events and errors from running the script and adds a header row.
if not os.path.exists('../aip_log.csv'):
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

# Uses the AIP functions to create an AIP for each folder in the metadata CSV.
# Checks if the AIP folder is still present before calling the function for the next step
# in case it was moved due to an error in the previous step.
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

    # Organizes the AIP folder contents into the UGA Libraries' AIP directory structure (objects and metadata).
    if aip.id in os.listdir('.'):
        a.structure_directory(aip)

    # Extracts technical metadata from the files using FITS.
    if aip.id in os.listdir('.'):
        a.extract_metadata(aip)
        a.combine_metadata(aip)

    # Converts the technical metadata into Dublin Core and PREMIS using xslt stylesheets.
    if aip.id in os.listdir('.'):
        a.make_cleaned_fits_xml(aip)
    if aip.id in os.listdir('.'):
        a.make_preservation_xml(aip)
    if aip.id in os.listdir('.'):
        a.validate_preservation_xml(aip)
    if aip.id in os.listdir('.'):
        a.organize_xml(aip)

    # Bags the AIP using bagit.
    if aip.id in os.listdir('.'):
        a.make_bag(aip)
        a.validate_bag(aip)

    # Tars the AIP and also zips (bz2) the AIP if ZIP (optional script argument) is True.
    if f'{aip.id}_bag' in os.listdir('.'):
        a.package(aip)

    # Adds the packaged AIP to the MD5 manifest in the aips-to-ingest folder.
    if f'{aip.id}_bag' in os.listdir('.'):
        a.manifest(aip)

# Closes the metadata CSV.
open_metadata.close()

print("\nScript is finished running.")
