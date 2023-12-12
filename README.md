# General Workflow for Creating AIPs

## Overview

This script implements the general workflow to make archival information packages (AIPs) that are ready for ingest 
into the UGA Libraries' digital preservation system (ARCHive). 
It may be used for one or multiple files of any file format.

AIPs contain digital objects and metadata files, including a preservation.xml file required by ARCHive,
and are bagged according to the Library of Congress standard. 
[UGA Libraries AIP Definition](https://docs.google.com/document/d/1PuRtSC9E0Fyt5vf4yVCER20bIWp_odPhdhGokBhJ69s/edit)

Specialized AIP workflows for audiovisual materials:
- [Brown Media Archives](https://github.com/uga-libraries/av-aip)
- [Russell Library Oral Histories](https://github.com/uga-libraries/av-aip_russell)

## Getting Started

### Dependencies

* bagit (https://github.com/LibraryOfCongress/bagit-python) - make bags
* FITS (https://projects.iq.harvard.edu/fits/downloads) - format identification and technical metadata
* md5deep (Windows only) (https://github.com/jessek/hashdeep/releases) - generate MD5 checksums
* pandas (https://pandas.pydata.org/docs/index.html) - analyze spreadsheets (unit tests only)
* saxon9he (http://saxon.sourceforge.net/) - transform XML using stylesheets
* Strawberry Perl (Windows only) (http://strawberryperl.com/) - to get xmllint (other use has been discontinued)
* xmllint (Windows only) (http://xmlsoft.org/xmllint.html) - validate XML using XSD files. Installed with Strawberry Perl.
* 7-Zip (Windows only) (https://www.7-zip.org/download.html) - tar and zip

### Installation

#### Configuration File

Use the configuration_template.py to make a file named configuration.py with file path variables for your local machine.

#### FITS Configuration

FITS includes multiple identification tools, and we adjust which tools are used for particular formats 
(based on the file extension) to reduce the number of errors.
1. Navigate to the "xml" folder in the FITS folder on your local machine.
2. Open the "fits.xml" file
3. Edit the "exclude-exts" and "include-exts" for each tool as needed.
    1. Jhove: exclude "warc"
    2. FileUtility: exclude "warc"

#### 7-Zip Path

For Windows, add 7-Zip to your Windows System PATH. 
In settings, go to Environment Variables > Path > Edit > New and add the 7-zip folder. 

#### Metadata File

Create a file named metadata.csv in the AIPs directory. [Example metadata.csv](documentation/metadata.csv) 
This contains required information about each of the AIPs to be included in this batch.
The header row is formatted Department,Collection,Folder,AIP_ID,Title,Version

For UGA, these values are:
* Department: ARCHive group name
* Collection: collection identifier
* Folder: the current folder name of the AIP folder
* AIP_ID: AIP identifier
* Title: AIP title
* Version: AIP version number, which must be a whole number

### Script Arguments

To run the script via the command line: python /path/general_aip.py aips_directory [no-zip]

* aips_directory (required) is the folder which contains all the folders to make into AIPs and the metadata.csv file
* no-zip (optional) is included to only tar and not zip the AIP (for big formats like disk images).

### Testing

Includes one test file per function, and a test to run the full script.
Unit test scripts should be run with the script repo folder "tests" as the current working directory.
Copy the configuration.py file for the local installation of the script to the "tests" folder before running any tests.

## Workflow
The workflow organizes the files, extracts and formats technical metadata, and bags and zips the AIP folders. 
Each AIP is fully processed before the next one is started.
If a known error is encountered, such as failing a validation test or a regular expression does not find a match, 
the AIP is moved to an error folder, and the rest of the steps are skipped for that AIP. 

1. Extracts the department, collection id, folder name, AIP id, title, and version from metadata.csv.


2. Deletes temporary files from anywhere within the AIP folder because they cause errors with validating bags.


3. Creates the AIP directory structure. 
   The AIP folder is named with the AIP ID and contains metadata and objects folders.

4. Extracts technical metadata from each file in the objects folder with FITS and saves the FITS xml to the metadata folder. 
   If there is more than one file with the same name, the FITS xml will include a number to distinguish between the different outputs. 
   Copies the information from each xml file into one file named combined-fits.xml, which is saved outside the AIP in the fits-xml folder.


5. Transforms the combined-fits xml into Dublin Core and PREMIS metadata using Saxon and an xslt stylesheet, 
   which is saved as preservation.xml in the metadata folder. 
   Verifies that the preservation.xml file meets UGA standards with xmllint and xsds.


6. Uses bagit to bag each AIP folder in place, making md5 and sha256 manifests. Validates the bag.


7. Tars and zips a copy of the bag, which is saved in the aips-to-ingest folder.


8. Uses md5deep to calculate the md5 for the packaged AIP and adds it to a department manifest in aips-to-ingest.

## Author

Adriane Hanson, Head of Digital Stewardship, December 2019.

## History

These scripts were adapted from a set of two bash scripts that were used for making AIPs from 2017-October 2019 at UGA Libraries. 
(https://github.com/uga-libraries/aip-mac-bash-fits)

