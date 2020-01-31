# Purpose: Creates PREMIS and Dublin Core metadata from the combined FITS metadata and saves it as a master.xml file that meets the metadata requirements for the UGA Libraries' digital preservation system (ARCHive).

# Dependencies: saxon, xmllint, xslt stylesheets, xsd schema files

import os
import shutil
import subprocess
import sys
from aip_variables import saxon, stylesheets, move_error


# The aip id, aip title, and department are arguments when this script is run from aips.py.
# The aip id is used to identify the folder the script should work on.
# The aip title and department are used by the stylesheet when making the master.xml.
aip = sys.argv[1]
aip_title = sys.argv[2]
department = sys.argv[3]

# workflow is used to indicate if the files are websites so the warc format designation can be used.
# It is passed as a parameter when running the stylesheets.
# A default value is assigned if there is no 4th argument.
if len(sys.argv) == 5:
    workflow = sys.argv[4]
else:
    workflow = 'general'


# Makes a simplified (cleaned) version of the combined fits xml with a stylesheet.
# Simplifies the structure, makes element order consistent, and removes empty elements.
# Saves the file in the aip's metadata folder. It will be deleted at the end of this script.
combined_fits = f'{aip}/metadata/{aip}_combined-fits.xml'
cleanup_stylesheet = f'{stylesheets}/fits-cleanup.xsl'
cleaned_fits = f'{aip}/metadata/{aip}_cleaned-fits.xml'

subprocess.run(f'java -cp {saxon} net.sf.saxon.Transform -s:"{combined_fits}" -xsl:"{cleanup_stylesheet}" -o:"{cleaned_fits}"', shell=True)


# Makes the master.xml file using a stylesheet and saves it to the aip's metadata folder.
# Selects the correct stylesheet for if the aip has one file or multiple files.
# If the objects folder is empty, moves the aip to an error folder and quits this script.

file_count = 0
for root, directories, files in os.walk(f'{aip}/objects'):
    file_count += len(files)

singlefile_stylesheet = f'{stylesheets}/fits-to-master_singlefile.xsl'
multifile_stylesheet = f'{stylesheets}/fits-to-master_multifile.xsl'
master_xml = f'{aip}/metadata/{aip}_master.xml'
     
if file_count == 1:
    subprocess.run(f'java -cp {saxon} net.sf.saxon.Transform -s:"{cleaned_fits}" -xsl:"{singlefile_stylesheet}" -o:"{master_xml}" aip-id="{aip}" aip-title="{aip_title}" department="{department}" workflow="{workflow}"', shell=True)

elif file_count == 0:
    move_error('no_files', folder)
    exit()

else:
    subprocess.run(f'java -cp {saxon} net.sf.saxon.Transform -s:"{cleaned_fits}" -xsl:"{multifile_stylesheet}" -o:"{master_xml}" aip-id="{aip}" aip-title="{aip_title}" department="{department}" workflow="{workflow}"', shell=True)

   
# Validates the master.xml file against the requirements of the UGA Libraries' digital preservation system (ARCHive).
# Possible validation errors: master.xml was not made (fail to loaded) or master.xml does not match the metadata requirements (fails to validate).
# If it is not valid, saves the validation error to a text document in the aip folder, moves the aip to an error folder, and quits this script.
validation = subprocess.run(f'xmllint --noout -schema "{stylesheets}/master.xsd" "{master_xml}"', stderr=subprocess.PIPE, shell=True)

if 'failed to load' in str(validation.stderr):
    with open(f'{aip}/masterxml_validation_error.txt', 'w') as error:
        error.write(str(validation.stderr))
    move_error('masterxml_not_made', aip)
    exit()

elif 'fails to validate' in str(validation.stderr):
    with open(f'{aip}/masterxml_validation_error.txt', 'w') as error:
        error.write(str(validation.stderr))
    move_error('masterxml_not_valid', aip)
    exit()


# Copies the master.xml to the master-xml folder for staff reference.
shutil.copy2(f'{aip}/metadata/{aip}_master.xml', '../master-xml')

         
# Moves the combined-fits.xml to the fits-xml folder for staff reference.
os.replace(f'{aip}/metadata/{aip}_combined-fits.xml', f'../fits-xml/{aip}_combined-fits.xml')


# Deletes the cleaned-fits.xml because it is a temporary file.
os.remove(f'{aip}/metadata/{aip}_cleaned-fits.xml')

