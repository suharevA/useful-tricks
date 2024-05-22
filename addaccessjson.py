import os
import yaml

class MyDumper(yaml.Dumper):
    """Increases the indentation level for the YAML output string."""
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

def decode_unicode_string(s):
    """Decodes a string or dictionary containing Unicode escape sequences."""
    if isinstance(s, str):
        return s.encode().decode('utf-8')
    elif isinstance(s, dict):
        return {k: decode_unicode_string(v) for k, v in s.items()}
    else:
        return s


path = 'backup'


for filename in os.listdir(path):
    if filename.endswith('.yml'):
        with open(os.path.join(path, filename), 'r') as file:
            try:
                data = yaml.safe_load(file)
                if data is None:
                    print(f"Warning: The file '{filename}' is empty or couldn't be parsed.")
                    continue

                for key in data:
                    updated_elements = []
                    for index, element in enumerate(data[key]):
                        # Decode Unicode escape sequences in the element
                        element = decode_unicode_string(element)
                        updated_elements.append(element)
                        # Check if the element contains 'access_log'
                        if 'access_log' in element:
                            # Extract the log name from the element without the .json extension
                            log_name = os.path.basename(element).split(' ')[0].rstrip('.json')
                            # Construct the new element string without appending .json
                            new_element = f"access_log /var/log/nginx/{log_name}.json extend_json"
                            # Check if the new element is already in the list
                            if new_element not in updated_elements:
                                # Insert the new element right after the current element
                                updated_elements.insert(index + 1, new_element)
                    # Update the data with the new list of elements
                    data[key] = updated_elements

                # Write the updated data back to the file
                with open(os.path.join(path, filename), 'w') as file:
                    decode_data = decode_unicode_string(data)
                    yaml.dump(decode_data, file, Dumper=MyDumper, default_flow_style=False, allow_unicode=True)


            except yaml.YAMLError as exc:
                print(f"Error parsing the file '{filename}': {exc}")
            except TypeError as exc:
                print(f"TypeError encountered while processing the file '{filename}': {exc}")
