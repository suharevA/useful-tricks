import os
import yaml

class MyDumper(yaml.Dumper):
    """Увеличивает уровень отступа для строки вывода YAML."""
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

path = 'backup'

for filename in os.listdir(path):
    if filename.endswith('.yml'):
        with open(os.path.join(path, filename), 'r') as file:
            data = yaml.safe_load(file)

        for key in data:
            updated_elements = []
            for element in data[key]:
                # Check if the element contains 'access_log'
                if 'access_log' in element:
                    # Extract the log name from the element without the.json extension
                    log_name = os.path.basename(element).split(' ')[0].rstrip('.json')
                    # Construct the new element string without appending.json
                    new_element = f"access_log /var/log/nginx/{log_name}.json extend_json"
                    # Append the new element to the updated_elements list
                    updated_elements.append(new_element)
                    print(f"Replaced element with '{new_element}'")
                else:
                    # If the element does not need to be replaced, append it as is
                    updated_elements.append(element)
            # Update the data with the new list of elements
            data[key] = updated_elements

        # Write the updated data back to the file
        with open(os.path.join(path, filename), 'w') as file:
            yaml.dump(data, file, Dumper=MyDumper, default_flow_style=False)
