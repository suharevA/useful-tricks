import os
import csv
import fnmatch, json, requests
from createconfig import CreateConfig
import re

responses = []


def listdir(pattern="*.csv"):
    """Find all *.csv files in the current directory"""
    j = fnmatch.filter(os.listdir('.'), pattern)
    return j


def read_csv():
    """Reads CSV and returns parameters in JSON format"""

    result = {}
    banned = ["www.mos.ru", "mos.ru", "school.mos.ru", "ag-vmeste.ru"]

    for file in listdir():
        with open(file, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';', skipinitialspace=True)
            for row in reader:
                domain = row.get('Доменное имя')
                if domain not in result:
                    result[domain] = {
                        "domain": {
                            "environment": row.get("Среда (production/stage/test)"),
                            "gost": row.get("Гост шифрование"),
                            "is_name": "Kubernetes",
                            "kms": row.get("Доступ только в КМС"),
                            "locations": [],
                            "name": domain
                        },
                        "format": "json"
                    }

                location = {
                    "kms": row.get("Доступ только в КМС"),
                    "path": row.get("Location"),
                    "upstreams": row.get("Upstream фронтенд").split(','),
                }

                waf = row.get("Upstream PTAF").split(',')
                if waf != ['']:
                    location.update(waf=waf)
                    for item in location["waf"]:
                        if isinstance(item, str) and ('/' in item or item.endswith('.') or item.endswith('_')):
                            raise ValueError('Некорректное значения поля "Upstream PTAF"')

                options = row.get("Прочее").split(',')
                if options != ['']:  # Check if options is not empty
                    location.update(options=options)

                # basic validation
                for ban in banned:
                    if ban == result[domain]['domain']['name']:
                        raise ValueError("Требуется обработать вручную доменное имя: " + ban)
                for item in location["upstreams"]:
                    if isinstance(item, str) and ('/' in item or item.endswith('.') or item.endswith('_')):
                        raise ValueError('Некорректное значения поля "Upstream фронтенд"')
                if not re.match(
                        r'^(?!.{255}|.{253}[^.])([a-z0-9](?:[-a-z-0-9]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[-a-z0-9]{0,61}[a-z0-9])?[.]?$',
                        result[domain]['domain']['name'], re.IGNORECASE):
                    raise ValueError('Некорректное значения поля "Доменное имя"')

                result[domain]['domain']['locations'].append(location)

                # принудительная замена значений в json
                gost = result[domain]['domain'].get('gost', '')
                kms = result[domain]['domain'].get('kms', '')
                kms_locations = result[domain]['domain'].get('locations', [])

                for item in kms_locations:
                    if item.get('kms', '') == 'нет':
                        item['kms'] = ''

                if kms.lower() == 'нет':
                    result[domain]['domain']['kms'] = ''

                if gost.lower() in ('нет', 'да'):
                    result[domain]['domain']['gost'] = ''

    # Convert the dictionary to a list of JSON objects
    json_objects = [value for key, value in result.items()]

    return json_objects


# Example usage:
def create_json():
    """Создает JSON-объект для данных каждого домена и
    отправляет его в виде POST-запроса на указанную конечную точку
    API."""
    domains_data = read_csv()
    for domain_data in domains_data:

        json_data = json.dumps(domain_data)
        # print(json_data)
        # print("================================================")
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post("http://balance.test-dc-cloud2.passport.local/api/v1/nginx_config",
                                 headers=headers, data=json_data)
        # print(response.text)
        json_data_validate = response.json()
        if json_data_validate is not None:
            error = json_data_validate.get('error', '')
            message = json_data_validate.get('message', '')
            # print(json_data_validate)

            error_responses = {
                'unknown directive': f"Неверное имя директивы для домена {domain_data['domain']['name']} {error}",
                'unexpected': f"Неверное имя директивы для домена {domain_data['domain']['name']} {error}",
                'cannot load certificate': f"Отсутствует сертификат для домена {domain_data['domain']['name']}",
                'host not found in upstream': f"{error}",
                'upstreams cannot be located': f"{message}"
            }

            if response.status_code == 200:
                config = CreateConfig()
                config.save_conf(json_data_validate, domain_data['domain']['name'])
                # config.consul(json_data_validate, domain_data['domain']['name'])
                responses.append({"message": f"{domain_data['domain']['name']} successfully", "nginx_output": True})
            else:
                for key, value in error_responses.items():
                    # print(error_responses.items())
                    if key in message:
                        responses.append({"message": value, "nginx_output": False})
                        break
    print(responses)


create_json()
