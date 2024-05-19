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
                # Check if the element matches the specific pattern
                if 'access_log /var/log/nginx/' in element and 'extend_json' in element:
                    # Skip adding elements that match the pattern to updated_elements
                    continue
                else:
                    # Add all other elements to updated_elements
                    updated_elements.append(element)
            # Update the data with the new list of elements
            data[key] = updated_elements

        # Write the updated data back to the file
        with open(os.path.join(path, filename), 'w') as file:
            yaml.dump(data, file, Dumper=MyDumper, default_flow_style=False)
