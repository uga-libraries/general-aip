"""Finish a single AIP that is already in bag form and has had some manual edits

This is typically used when the preservation.xml needs to be edited to clean up format identifications
or address special characters that cannot be ingested into our preservation system.

To correct, validate the bag and edit as needed. Then run this script, which will have it ready to ingest into ARCHive.
The script will add to a manifest.txt file in the parent folder of the bag, so multiple AIPs can be ingested as a batch.

Parameter:
    bag_path (required): path to the bag to be finished into an AIP

Returns:
    .tar.bz2 version of the AIP ready to ingest into the preservation system
    manifest.txt with the md5 of the AIP needed for ingest
"""
import bagit
import os
import subprocess
import sys


def package_bag(bag_path, bag):
    """Tar, add the size to the filename, and bz2
    Parameters:
        bag_path (string) - path to bag
        bag (bagit Bag) - bag instance for extracting bag payload
    Returns: zip_path (string) - path to the zipped bag
    """

    # Gets the total size in bytes of the bag: bag payload (data folder) from bag-info.txt plus bag metadata files.
    bag_payload = bag.info['Payload-Oxum']
    bag_size = bag_payload.load.split('.')[0]
    for file in os.listdir(bag_path):
        if file.endswith(".txt"):
            bag_size += os.path.getsize(os.path.join(bag_path, file))
    bag_size = int(bag_size)

    # Tars the file without printing progress to the terminal (stdout).
    subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -ttar a "{bag_path}.tar" "{bag_path}"',
                   stdout=subprocess.DEVNULL, shell=True)

    # Renames the file to include the size.
    tar_size_path = f"{bag_path}.{bag_size}.tar"
    os.replace(f"{bag_path}.tar", tar_size_path)

    # Zips (bz2) the tar file without printing progress to the terminal (stdout).
    subprocess.run(f'"C:/Program Files/7-Zip/7z.exe" -tbzip2 a -aoa "{tar_size_path}.bz2" "{tar_size_path}"',
                   stdout=subprocess.DEVNULL, shell=True)

    # Deletes the tar version. Just want the tarred and zipped version.
    os.remove(tar_size_path)

    # Returns the path to the zip for adding it to the manifest.
    return f"{tar_size_path}.bz2"


def validate_bag(bag):
    """Validate the bag and print the result for the log
    Parameter: bag (bagit Bag) - bag to be validated
    Returns: is_valid (Boolean)"""
    try:
        bag.validate()
        return True
    except (bagit.BagValidationError, bagit.BagError) as error_msg:
        print("Bag is not valid - cannot complete rest of the script")
        print(error_msg)
        return False


if __name__ == '__main__':

    # Get path to the bag to be made into a finished AIP (script argument) and read as a Bag.
    bag_path = sys.argv[1]
    bag_instance = bagit.Bag(bag_path)

    # Update the bag.
    bag_instance.save(manifests=True)

    # Validate the bag. If the bag is not valid, exit the script.
    bag_valid = validate_bag(bag_instance)
    if not bag_valid:
        sys.exit(1)

    # Package (tar and zip) the bag, including add the unzipped size to the filename.
    zip_path = package_bag(bag_path, bag_instance)
