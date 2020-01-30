# General Workflow for AIPs

# Purpose and overview
This is the general workflow to make archival information packages (aips) that are ready for ingest into the UGA Libraries' digital preservation system (ARCHive). The workflow organizes files, extracts and formats metadata, and packages the files. It may be used for any combination of file formats. More specialized workflows have been developed for [audiovisual materials](https://github.com/uga-libraries/av-aip_russell) and [web archives](https://github.com/uga-libraries/web-aip). 

# Script approach
Each step of the workflow is in its own Python script. The script aips.py is used to iterate over the folders being made into aips, calling the script for each step in turn. Each aip is fully processed before the next one is started. This modular approach makes it easier to set up variations on the workflow by not running a step or substituting a different script for a step in aips.py. It also makes it easier to find and edit code since each script is small and has a clear purpose.

# Error handling
If a known error is encountered, such as failing a validation test or a regular expression does not find a match, the aip is moved to an error folder with the name of the error and the rest of the steps are skipped for that aip. 

# Script usage
python3 /path/aips.py /path/aip-directory department
* aips.py is the script that controls the workflow and calls the other scripts.
* aip-directory is the folder which contains all the folders to make into aips.
* department is used to match department identifier patterns. Otherwise, the workflow is the same for all departments.

# Dependencies
* Mac or Linux operating system
* bagit.py (https://github.com/LibraryOfCongress/bagit-python)
* FITS (https://projects.iq.harvard.edu/fits/downloads)
* md5deep (https://github.com/jessek/hashdeep)
* saxon9he (http://saxon.sourceforge.net/)
* xmllint (http://xmlsoft.org/xmllint.html)

# Installation
1. Install the dependencies (listed above). Saxon and md5deep may be come with your OS.


2. Download the scripts and stylesheets folders and save to your computer.
3. Update the file path variables (lines 14-17) in the aip_variables.py script for your local machine.
4. Update the base uri in the stylesheets and premis.xsd to the base for your identifiers where it says "INSERT-URI".
    * fits-to-master_multifile.xsl: in variable name="uri" (line 60)
    * fits-to-master_singlefile.xsl: in variable name="uri" (line 66)
    * premis.xsd: in restriction pattern for objectIdentifierType (line 42)
5. Change permission on the scripts so they are executable.

# Workflow Details
1. Deletes temporary files from anywhere within the aip folder because they cause errors with validating bags. (directory.py)
2. Creates the aip directory. The aip folder has the naming convention aip-id_AIP Title and contains metadata and objects folders. The digital content is moved to the objects folder.  (directory.py)
3. Extracts technical metadata from each file in the objects folder with FITS and saves the FITS xml to the metadata folder. 4. Copies the information from each xml file into one file named combined-fits.xml, also saved in the metadata folder. (fits.py)
5. Transforms the combined-fits xml into PREMIS metadata using Saxon and xslt stylesheets, which is saved as master.xml in the metadata folder. Verifies that the master.xml file meets UGA standards with xmllint and xsds. (master_xml.py)
6. Uses bagit.py to bag each aip folder in place, making md5 and sha256 manifests. Validates the bag. (package.py)
7. Uses the prepare_bag perl script to tar and zip a copy of the bag, which is saved in the aips-to-ingest folder. (package.py)
8. Once all aips are created, uses md5deep to calculate the md5 for each packaged aip and saves it to a manifest, along with the filename. (aips.py)

# Initial Author
Adriane Hanson, Head of Digital Stewardship, December 2019.

# Acknowledgements
These scripts were adapted from a set of two bash scripts that were used for making aips from 2017-October 2019 at UGA Libraries. (https://github.com/uga-libraries/aip-mac-bash-fits)

