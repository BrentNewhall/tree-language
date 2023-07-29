import os
import subprocess
import difflib

def fix_line_endings(data):
    return data.replace('\r\n', '\n').replace('\r', '\n')

def test_file(filename):
    # Calculate the expected output filename.
    expected_filename = filename[:-3] + '.to'
    # Check for existince of corresponding .to file.
    if not os.path.exists(expected_filename):
        print('No .to file found for', filename)
        return
    # Get .to file contents.
    with open(expected_filename) as f:
        expected = fix_line_endings( f.read().rstrip() )
    # Execute the code in filename and capture the output.
    output = subprocess.check_output(['python', 'run.py', '--file', filename])
    # Convert the output from bytes to a string.
    output = fix_line_endings( output.decode('utf-8').rstrip() )
    # Compare the output to the expected output.
    if output.strip() != expected.strip():
        print('##### END FAILURE:', filename)
        # Use difflib's context_diff to print a diff of the two outputs.
        diff = difflib.context_diff(expected.splitlines(), output.splitlines(), fromfile=expected_filename, tofile=filename)
        print('\n'.join(diff))
    else:
        print('##### END SUCCESS:', filename)

# Find all files ending in .tc and run them as test cases.
for filename in os.listdir('.'):
    if filename.endswith('.tc'):
        print('##### BEGIN TEST CASE:', filename)
        test_file(filename)
        print()