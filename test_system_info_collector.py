import subprocess
import os
import sys

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

    # Using /app as start_path for faster execution and manageable output
    result = run_main_script(TEST_OUTPUT_FILENAME, start_path="/app")

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

if __name__ == "__main__":
    try:
        test_successful_execution_and_file_creation()
        test_content_verification()
        print("All tests PASSED successfully!")
    except AssertionError as e:
        print(f"TEST FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"AN UNEXPECTED ERROR OCCURRED DURING TESTING: {e}", file=sys.stderr)
        sys.exit(2)
