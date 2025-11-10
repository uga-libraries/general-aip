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
* Java (https://www.java.com/en/download/) - for running FITS
* md5deep (Windows only) (https://github.com/jessek/hashdeep/releases) - generate MD5 checksums
* pandas (https://pandas.pydata.org/docs/index.html) - analyze spreadsheets (unit tests only)
* saxon9he (http://saxon.sourceforge.net/) - transform XML using stylesheets
* Strawberry Perl (Windows only) (http://strawberryperl.com/) - to get xmllint (other use has been discontinued)
* xmllint (Windows only) (http://xmlsoft.org/xmllint.html) - validate XML using XSD files. Installed with Strawberry Perl.
* 7-Zip (Windows only) (https://www.7-zip.org/download.html) - tar and zip

### Installation

#### Configuration File

Use the configuration_template.py to make a file named configuration.py with file path variables for your local machine.

The path to FITS in configuration.py MUST be in the same letter directory as the files being converted to AIPs.

#### FITS Configuration

FITS includes multiple identification tools, and we adjust which tools are used for particular formats 
(based on the file extension) to reduce the number of errors.
1. Navigate to the "xml" folder in the FITS folder on your local machine.
2. Open the "fits.xml" file
3. Edit the "exclude-exts" and "include-exts" for each tool as needed.
    1. Jhove: exclude "warc"
    2. FileUtility: exclude "warc"
4. Comment out (start with <!-- and end with -->) MediaInfo, which has a known issue of not running correctly in FITS.

#### 7-Zip Path

For Windows, add 7-Zip to your Windows System PATH. 
In settings, go to Environment Variables > Path > Edit > New and add the 7-zip folder. 

#### Metadata File

Create a file named metadata.csv in the AIPs directory. [Example metadata.csv](documentation/metadata.csv) 
This contains required information about each of the AIPs to be included in this batch.
The header row is formatted Department,Collection,Folder,AIP_ID,Title,Rights,Version

For UGA, these values are:
* Department: ARCHive group name
* Collection: collection identifier
* Folder: the current folder name of the AIP folder
* AIP_ID: AIP identifier
* Title: AIP title
* Rights: either Creative Commons license or RightsStatements.org statement
* Version: AIP version number, which must be a whole number

#### Changing Rights Statements

By default, the fits-to-preservation.xsl stylesheet will assign http://rightsstatements.org/vocab/InC/1.0/ to the AIPs.
To change this, edit the stylesheet prior to running the script.
There must be one rightstatement.org or Creative Commons license.

For additional rights, add one <dc:rights> element per rights statement.
The right must be added to our preservation system (ARCHive) first.
The element value is the objectIdentifierType/objectIdentifierValue from our preservation system.

### Script Arguments

To run the script via the command line: python /path/general_aip.py aips_directory [no-zip]

* aips_directory (required) is the folder which contains all the folders to make into AIPs and the metadata.csv file
* no-zip (optional) is included to only tar and not zip the AIP (for big formats like disk images).

### Testing

Includes one test file per function, and a test to run the full script.
Unit test scripts should be run with the script repo folder "tests" as the current working directory.

Before running test_check_configuration.py (test is commented out by default to not run with the full test suite), 
rename the configuration_test.py file in the tests folder to configuration.py
and rename it back to configuration_test.py once the test is complete.
Otherwise, the wrong configuration.py is used for all other tests.

The test for av in test_manifest.py only works on a Mac, because it requires rysnc.
The test is commented out by default to not cause errors in Windows.

When the script is updated, it is changing the date last modified of test files, which is part of the deletion log.
This impacts tests for delete_temp and the script.

Known issue: Tests that check the contents of XML may fail due to the inconsistent order of element attributes.

## Workflow

The script organizes the files, extracts and formats technical metadata, and bags and zips the AIP folders.
See [AIP Creation Instructions](documentation/aip_creation_instructions.md) for details.

Each AIP is fully processed before the next one is started.
If a known error is encountered, such as failing a validation test or a regular expression does not find a match, 
the AIP is moved to an error folder, and the rest of the steps are skipped for that AIP.

## Author

Adriane Hanson, Head of Digital Stewardship, December 2019.

## History

These scripts were adapted from a set of two bash scripts that were used for making AIPs from 2017-October 2019 at UGA Libraries. 
(https://github.com/uga-libraries/aip-mac-bash-fits)
