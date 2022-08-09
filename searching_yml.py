# поиск файла по имени, чтение

path='.'
domen = """

"""
for d in domen.split():
    for rootdir, dirs, files in os.walk(path):
        for file in files:
            if file == f'{d}_9443.yml':
                print(f'{rootdir}/{file}')
                with open(f'{rootdir}/{file}') as f:
                    templates = yaml.safe_load(f)
                    for keys, values in templates.items():
                        for v in values:
                            print(v)
