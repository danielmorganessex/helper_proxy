import subprocess
import os
import sys
import tempfile
import shutil

# Use the same Python interpreter for the subprocess that is running this test script
PYTHON_EXECUTABLE = sys.executable
MAIN_SCRIPT_PATH = "system_info_collector.py"
TEST_OUTPUT_FILENAME = "test_run_output.txt"

def run_main_script(output_filename, start_path=None):
    """Helper function to run the main script with specified arguments."""
    command = [PYTHON_EXECUTABLE, MAIN_SCRIPT_PATH, output_filename]
    if start_path:
        command.extend(["--start_path", start_path])
    return subprocess.run(command, capture_output=True, text=True)

def cleanup_test_file():
    """Removes the test output file if it exists."""
    if os.path.exists(TEST_OUTPUT_FILENAME):
        os.remove(TEST_OUTPUT_FILENAME)

def test_successful_execution_and_file_creation():
    """
    Test 1: Successful execution and output file creation.
    - Runs system_info_collector.py.
    - Asserts that the script exits with code 0.
    - Asserts that the temporary output file is created.
    - Cleans up by removing the temporary output file.
    """
    print("Running Test 1: Successful execution and file creation...")
    cleanup_test_file() # Ensure no old file exists

    result = run_main_script(TEST_OUTPUT_FILENAME)

    print(f"  stdout:\n{result.stdout}")
    print(f"  stderr:\n{result.stderr}")

    assert result.returncode == 0, f"Script exited with {result.returncode}, expected 0."
    print("  Asserted: Script exited with code 0.")

    assert os.path.exists(TEST_OUTPUT_FILENAME), f"Output file '{TEST_OUTPUT_FILENAME}' was not created."
    print(f"  Asserted: Output file '{TEST_OUTPUT_FILENAME}' created.")

    cleanup_test_file()
    print(f"  Cleaned up '{TEST_OUTPUT_FILENAME}'.")
    print("Test 1 PASSED.\n")

def test_content_verification():
    """
    Test 2: Content verification.
    - Runs system_info_collector.py again.
    - Reads the content of the output file.
    - Asserts that key section headers are present.
    - Asserts that a known environment variable ('PATH=') is present.
    - Cleans up the temporary output file.
    """
    print("Running Test 2: Content verification...")
    cleanup_test_file() # Ensure no old file exists

    # Using "." (current directory) as start_path for faster execution and manageable output
    result = run_main_script(TEST_OUTPUT_FILENAME, start_path=".")

    assert result.returncode == 0, f"Script exited with {result.returncode}, expected 0 (for content test run)."

    assert os.path.exists(TEST_OUTPUT_FILENAME), f"Output file '{TEST_OUTPUT_FILENAME}' was not created (for content test run)."

    content = ""
    with open(TEST_OUTPUT_FILENAME, 'r') as f:
        content = f.read()

    expected_headers = [
        "=== System Information ===",
        "=== Environment Variables ===",
        "=== Filesystem Paths ==="
    ]
    for header in expected_headers:
        assert header in content, f"Expected header '{header}' not found in output."
    print(f"  Asserted: All expected headers {expected_headers} found.")

    # Check for a common environment variable. PATH is very likely to exist.
    # The main script writes "KEY: VALUE", so we search for "PATH: "
    expected_env_var_substring = "PATH: "
    path_assertion_passed = expected_env_var_substring in content
    if not path_assertion_passed:
        print(f"  DEBUG: '{expected_env_var_substring}' not found. Actual content block for env vars:\n------\n")
        env_vars_section = content.split("=== Environment Variables ===")[1].split("=== Filesystem Paths ===")[0]
        print(env_vars_section)
        print("------")
    assert path_assertion_passed, f"Expected environment variable substring '{expected_env_var_substring}' not found in output."
    print(f"  Asserted: Environment variable substring '{expected_env_var_substring}' found.")

    cleanup_test_file()
    print(f"  Cleaned up '{TEST_OUTPUT_FILENAME}'.")
    print("Test 2 PASSED.\n")

def test_multiple_start_paths():
    """
    Test 3: Multiple start paths functionality.
    - Creates temporary directories and unique files within them.
    - Runs system_info_collector.py with --start_path set to these directories.
    - Verifies script success and checks if unique files are listed in the output.
    - Cleans up temporary directories and the output file.
    """
    print("Running Test 3: Multiple start paths...")
    cleanup_test_file()

    # Create temporary directories for testing multiple paths
    with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
        # Create unique files in each directory
        file_in_tmpdir1_abs = os.path.join(tmpdir1, "fileA_in_tmp1.txt")
        file_in_tmpdir2_abs = os.path.join(tmpdir2, "fileB_in_tmp2.txt")

        with open(file_in_tmpdir1_abs, "w") as f:
            f.write("Test content for file A")
        with open(file_in_tmpdir2_abs, "w") as f:
            f.write("Test content for file B")

        # Construct the comma-separated start_path argument
        multiple_start_paths = f"{tmpdir1},{tmpdir2}"

        result = run_main_script(TEST_OUTPUT_FILENAME, start_path=multiple_start_paths)

        print(f"  stdout:\n{result.stdout}")
        print(f"  stderr:\n{result.stderr}")

        assert result.returncode == 0, f"Script exited with {result.returncode}, expected 0 for multiple paths test."
        print("  Asserted: Script exited with code 0.")

        assert os.path.exists(TEST_OUTPUT_FILENAME), f"Output file '{TEST_OUTPUT_FILENAME}' was not created for multiple paths test."
        print(f"  Asserted: Output file '{TEST_OUTPUT_FILENAME}' created.")

        content = ""
        with open(TEST_OUTPUT_FILENAME, 'r') as f:
            content = f.read()

        # Verify that the unique file paths are present in the "Filesystem Paths" section
        # We need to find the section first.
        filesystem_section_header = "=== Filesystem Paths ==="
        assert filesystem_section_header in content, f"'{filesystem_section_header}' not found in output."

        # Normalize paths for comparison, especially on Windows
        normalized_content = content.replace("\\", "/")
        normalized_file_in_tmpdir1 = file_in_tmpdir1_abs.replace("\\", "/")
        normalized_file_in_tmpdir2 = file_in_tmpdir2_abs.replace("\\", "/")

        # Check if the paths are present in the content after the header
        filesystem_paths_text = normalized_content.split(filesystem_section_header, 1)[1]

        assert normalized_file_in_tmpdir1 in filesystem_paths_text, f"Path '{file_in_tmpdir1_abs}' (normalized: {normalized_file_in_tmpdir1}) not found in filesystem paths output."
        print(f"  Asserted: Path '{file_in_tmpdir1_abs}' found.")
        assert normalized_file_in_tmpdir2 in filesystem_paths_text, f"Path '{file_in_tmpdir2_abs}' (normalized: {normalized_file_in_tmpdir2}) not found in filesystem paths output."
        print(f"  Asserted: Path '{file_in_tmpdir2_abs}' found.")

    # Temporary directories are cleaned up automatically by TemporaryDirectory context manager
    cleanup_test_file()
    print(f"  Cleaned up '{TEST_OUTPUT_FILENAME}'. Temporary directories also cleaned up.")
    print("Test 3 PASSED.\n")


if __name__ == "__main__":
    try:
        test_successful_execution_and_file_creation()
        test_content_verification()
        test_multiple_start_paths()
        print("All tests PASSED successfully!")
    except AssertionError as e:
        print(f"TEST FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"AN UNEXPECTED ERROR OCCURRED DURING TESTING: {e}", file=sys.stderr)
        sys.exit(2)
