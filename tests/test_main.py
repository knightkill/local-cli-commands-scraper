import os
import csv


# Function to check if the output file has been created and contains data
def test_script():
    output_dir = "./output"
    if not os.path.exists(output_dir):
        print("Output directory does not exist.")
        return False

    files = os.listdir(output_dir)
    if not files:
        print("No files found in the output directory.")
        return False

    output_file = os.path.join(output_dir, files[0])
    if not os.path.isfile(output_file):
        print(f"Output file {output_file} does not exist.")
        return False

    with open(output_file, mode='r') as file:
        reader = csv.reader(file, delimiter='|')
        rows = list(reader)
        if len(rows) < 2:
            print("Output file does not contain enough data.")
            return False

    print(f"Test passed. Descriptions added to {output_file}")
    return True


# Run the test
test_script()
