# General Workflow for AIPs

# Purpose and overview
This is the general workflow to make archival information packages (AIPs) that are ready for ingest into the UGA Libraries' digital preservation system (ARCHive). The workflow organizes the files, extracts and formats metadata, and packages the files. It may be used for one or multiple files of any file format. More specialized workflows have been developed for [audiovisual materials](https://github.com/uga-libraries/av-aip_russell) and [web archives](https://github.com/uga-libraries/web-aip). 

# Script approach
Each step of the workflow is in its own Python function. The functions are in a separate document (aip_functions.py) so that these can easily be used in other workflows as well. The general aip workflow is implemented by general_aip.py, which iterates over the folders being made into AIPs, calling the function for each step in turn. Each AIP is fully processed before the next one is started.

If a known error is encountered, such as failing a validation test or a regular expression does not find a match, the AIP is moved to an error folder with the name of the error and the rest of the steps are skipped for that AIP. A log is also created as the script runs which saves details about the errors. 

# Script usage
python /path/general_aip.py /path/aip-directory
* general_aip.py is the script that implements the workflow.
* aip-directory is the folder which contains all the folders to make into AIPs.

# Dependencies
md5deep and xmllint are pre-installed on some operating systems.
* bagit.py (https://github.com/LibraryOfCongress/bagit-python)
* FITS (https://projects.iq.harvard.edu/fits/downloads)
* md5deep (https://github.com/jessek/hashdeep)
* saxon9he (http://saxon.sourceforge.net/)
* Strawberry Perl (Windows only) (http://strawberryperl.com/)
* xmllint (http://xmlsoft.org/xmllint.html)
* 7-Zip (Windows only) (https://www.7-zip.org/download.html)

# Installation
1. Install the dependencies (listed above).


2. Download this repository and save to your computer.
3. Update the file path variables (lines 14-18) in the aip_functions.py script with the paths for your local machine.
4. Update the base uri in the stylesheets and premis.xsd to the base for your identifiers where it says "INSERT-URI".
    * fits-to-master_multifile.xsl: in variable name="uri" (line 60)
    * fits-to-master_singlefile.xsl: in variable name="uri" (line 66)
    * premis.xsd: in restriction pattern for objectIdentifierType (line 42)
5. Change permission on the scripts so they are executable.

# Workflow Details
1. Extracts teh aip id, department, and aip title from the aip folder title.


2. Deletes temporary files from anywhere within the aip folder because they cause errors with validating bags.
3. Creates the aip directory. The aip folder has the naming convention aip-id_AIP Title and contains metadata and objects folders. The digital content is moved to the objects folder.
4. Extracts technical metadata from each file in the objects folder with FITS and saves the FITS xml to the metadata folder. Copies the information from each xml file into one file named combined-fits.xml, also saved in the metadata folder.
5. Transforms the combined-fits xml into Dublin Core and PREMIS metadata using Saxon and xslt stylesheets, which is saved as master.xml in the metadata folder. Verifies that the master.xml file meets UGA standards with xmllint and xsds.
6. Uses bagit to bag each aip folder in place, making md5 and sha256 manifests. Validates the bag.
7. Uses a perl script to tar and zip a copy of the bag, which is saved in the aips-to-ingest folder.
8. Once all AIPs are created, uses md5deep to calculate the md5 for each packaged AIP and saves it to a manifest, along with the filename.

# Initial Author
Adriane Hanson, Head of Digital Stewardship, December 2019.

# Acknowledgements
These scripts were adapted from a set of two bash scripts that were used for making aips from 2017-October 2019 at UGA Libraries. (https://github.com/uga-libraries/aip-mac-bash-fits)

