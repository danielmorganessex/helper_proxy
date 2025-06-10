import os
import shutil
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def recursive_copy_function(source_dir, dest_dir):
    """
    Recursively copies a directory from source_dir to dest_dir.
    This function will be implemented in a later step.
    For now, it just logs the intention.
    """
    logging.info(f"Starting copy from '{source_dir}' to '{dest_dir}'.")
    try:
        # Ensure the parent of dest_dir exists if dest_dir itself is a new directory name
        # within an existing path. shutil.copytree creates dest_dir, but not its parents.
        parent_dest = os.path.dirname(dest_dir)
        if parent_dest and not os.path.exists(parent_dest):
            os.makedirs(parent_dest)
            logging.info(f"Created parent destination directory: {parent_dest}")

        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True) # Requires Python 3.8+
        logging.info(f"Successfully copied '{source_dir}' to '{dest_dir}'.")
    except FileExistsError as e:
        # This should ideally be handled by dirs_exist_ok=True in Python 3.8+
        # but good to be aware if an older Python version was used without dirs_exist_ok.
        logging.error(f"FileExistsError: Destination '{dest_dir}' already exists and is a file, or source is a file and dest exists. {e}")
    except NotADirectoryError as e:
        logging.error(f"NotADirectoryError: A component of the path is not a directory. {e}")
    except PermissionError as e:
        logging.error(f"PermissionError: Permission denied during copy. {e}")
    except OSError as e:
        logging.error(f"OSError during copy: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during copy: {e}")

def main():
    parser = argparse.ArgumentParser(description="Recursively copy a directory.")
    parser.add_argument("source_directory", help="The source directory to copy from.")
    parser.add_argument("destination_directory", help="The destination directory to copy to.")

    args = parser.parse_args()

    source_path = os.path.abspath(args.source_directory)
    destination_path = os.path.abspath(args.destination_directory)

    logging.info(f"Source directory: {source_path}")
    logging.info(f"Destination directory: {destination_path}")

    if not os.path.exists(source_path):
        logging.error(f"Source directory '{source_path}' does not exist.")
        return

    if not os.path.isdir(source_path):
        logging.error(f"Source '{source_path}' is not a directory.")
        return

    recursive_copy_function(source_path, destination_path)

if __name__ == "__main__":
    main()
