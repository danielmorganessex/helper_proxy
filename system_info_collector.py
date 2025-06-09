import platform
import psutil
import subprocess
import os
import sys
import argparse

def get_system_info():
    """Gathers basic system information."""
    info = {}
    info['platform'] = platform.system()
    info['platform_release'] = platform.release()
    info['platform_version'] = platform.version()
    info['architecture'] = platform.machine()
    info['hostname'] = platform.node()
    info['processor'] = platform.processor()
    info['ram'] = str(round(psutil.virtual_memory().total / (1024.0 **3))) + " GB"
    return info

def _handle_walk_error(err):
    """Error handler for os.walk, prints to stderr and continues."""
    print(f"PermissionError accessing: {err.filename}. Skipping.", file=sys.stderr)

def get_filesystem_info(start_paths=None):
    """Traverses the filesystem from the specified start_paths and collects all file and directory paths."""
    if start_paths is None:
        start_paths = ["/"]
    all_paths = []
    for start_path in start_paths:
        for root, dirs, files in os.walk(start_path, onerror=_handle_walk_error):
            for name in files:
                try:
                    path = os.path.join(root, name)
                    all_paths.append(path)
                except Exception as e: # Catch potential errors from os.path.join itself, though rare
                    print(f"Error joining path ({root}, {name}): {e}", file=sys.stderr)
            for name in dirs:
                try:
                    path = os.path.join(root, name)
                    all_paths.append(path)
                except Exception as e:
                    print(f"Error joining path ({root}, {name}): {e}", file=sys.stderr)
    return all_paths

def get_environment_variables():
    """Retrieves all environment variables."""
    # os.environ is a dict-like object, convert it to a standard dict
    return dict(os.environ)

def save_data_to_file(filepath, system_info_data, env_vars_data, filesystem_data):
    """Saves the collected data to the specified file."""
    try:
        with open(filepath, 'w') as f:
            f.write("=== System Information ===\n")
            for key, value in system_info_data.items():
                f.write(f"{key}: {value}\n")

            f.write("\n=== Environment Variables ===\n")
            for key, value in env_vars_data.items():
                f.write(f"{key}: {value}\n")

            f.write("\n=== Filesystem Paths ===\n")
            f.write(f"(Total paths: {len(filesystem_data)})\n")
            # Limit writing paths to the file to avoid excessively large files.
            limit_paths = 1000
            if not filesystem_data:
                f.write("No filesystem paths collected or provided.\n")
            for i, path in enumerate(filesystem_data):
                if i < limit_paths:
                    f.write(f"{path}\n")
                else:
                    f.write(f"... and {len(filesystem_data) - limit_paths} more paths truncated.\n")
                    break
    except IOError as e:
        print(f"Error writing to file {filepath}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while saving data to {filepath}: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collects system information and saves it to a specified file.")
    parser.add_argument("output_filepath", help="Path to the output file where information will be saved.")
    parser.add_argument("--start_path", default="/", help="Comma-separated list of starting paths for filesystem traversal (e.g., /app,/usr). Defaults to '/'.")
    args = parser.parse_args()

    # Split the start_path argument into a list
    start_paths_list = [path.strip() for path in args.start_path.split(',')]

    # Collect all data
    system_info_data = get_system_info()
    environment_vars_data = get_environment_variables()

    print(f"Starting filesystem traversal from '{', '.join(start_paths_list)}'. This may take some time and report permission errors...", file=sys.stderr)
    filesystem_paths_data = get_filesystem_info(start_paths_list)
    print("Filesystem traversal complete.", file=sys.stderr)

    # Print basic system info to console
    for key, value in system_info_data.items():
        print(f"{key}: {value}")

    # Save all collected data to a file (filename from command line)
    save_data_to_file(args.output_filepath, system_info_data, environment_vars_data, filesystem_paths_data)
    print(f"\nAll collected data saved to {args.output_filepath}")
    print(f"Total filesystem paths collected from '{', '.join(start_paths_list)}': {len(filesystem_paths_data)}")
    print(f"Total environment variables collected: {len(environment_vars_data)}")
