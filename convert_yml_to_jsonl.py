import os
import json
import yaml


def convert_yaml_to_jsonl(input_directory, output_file):
    # Check if the directory exists
    if not os.path.isdir(input_directory):
        print(f"The directory {input_directory} does not exist.")
        return

    # Open the output file for writing results
    with open(output_file, 'w', encoding='utf-8') as jsonl_file:
        # Iterate through all files in the directory
        for filename in os.listdir(input_directory):
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                # Construct the full file path
                filepath = os.path.join(input_directory, filename)

                # Read the YAML file content
                with open(filepath, 'r', encoding='utf-8') as yaml_file:
                    try:
                        # Load YAML and convert to JSON
                        yaml_content = yaml.safe_load(yaml_file)
                        json_content = json.dumps(yaml_content, ensure_ascii=False)

                        # Write the JSON to the .jsonl file
                        jsonl_file.write(json_content + '\n')
                        print(f"File {filename} has been successfully converted and added to {output_file}.")
                    except yaml.YAMLError as e:
                        print(f"Error reading file {filename}: {e}")
                    except json.JSONDecodeError as e:
                        print(f"Error converting file {filename} to JSON: {e}")

    print("Conversion completed.")


# Run the function
convert_yaml_to_jsonl('characters', 'characters.jsonl')
