import os
import shutil
import sys


def copy_files_with_extension(source_dir, destination_dir, file_extension):
    # Check if the source directory exists
    if not os.path.isdir(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        sys.exit(1)

    # Create the destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)

    # Iterate through the files in the source directory
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(file_extension):
                # Construct full file paths
                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination_dir, file)

                # Copy the file to the destination directory
                shutil.copy2(source_file, destination_file)
                print(f"Copied: {file}")

    print(f"All '{file_extension}' files have been copied from '{source_dir}' to '{destination_dir}'.")

if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 4:
        print("Usage: python copy_files.py /path/to/source /path/to/destination .file_extension")
        sys.exit(1)

    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]
    file_extension = sys.argv[3]

    copy_files_with_extension(source_dir, destination_dir, file_extension)