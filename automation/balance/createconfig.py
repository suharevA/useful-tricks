import requests
import yaml
import consul
import logging

paths_folder = 'mosru_nginx/mos_ru_nginx'
skdpu_http_upstreams = f'{paths_folder}/skdpu_config/skdpu_http_upstreams.yml'
skdpu_tcp_var_backend = f'{paths_folder}/skdpu_config/skdpu_tcp_var_backend.yml'

logging.basicConfig(level=logging.INFO)
class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

def mv_config(dc, env):
    """ Перемещаем в нужную папку """
    if env:
        if dc == 'kur':
            move_path = f'{paths_folder}/{env}_sites'
        elif dc == 'kor':
            move_path = f'{paths_folder}/{env}_kor_sites'
        else:
            move_path = None

        if move_path:
            print(f'сохраняю в {move_path}')
            return move_path
    return None


class CreateConfig:
    """Принимаем параметры из sendcsv и создаем конфиг"""

    def save_conf(self, config, domain):
        """Сохраняем конфиг"""
        with open(skdpu_http_upstreams) as f:
            templates = yaml.safe_load(f)
            for keys, values in templates.items():
                upstreams = tuple(config.get('upstreams_config'))
                for records in upstreams:
                    if records in values:
                        print(f"В skdpu_config запись {records} найдена...\n")
                        # print(values.get(records))
                        # print(config.get('upstreams_config').get(records))

                        values[records].update(config['upstreams_config'][records])
                    else:
                        print(f"В skdpu_config запись {records} не найдена...\n")
                        values[records] = config['upstreams_config'][records]

        # Запись обновленных значений в файл
        with open(skdpu_http_upstreams, "w") as f:
            yaml.dump(templates, f)

        catalog = mv_config(config['dc'], config['environment'])
        # print(config['site_config'])
        # print(config['site_config'].get(f'{domain}_9443'))

        with open(f'{catalog}/{domain}_9443.yml', 'w') as file:
            yaml.dump(config['site_config'], file, Dumper=MyDumper, default_flow_style=False)
        return {"updated": f"{domain}"}
#
    #             if self.gost == 'да':
    #                 tcp_var = f'  {self.domains}:\n    gost_upstream: ngate_prod'
    #                 with open(skdpu_tcp_var_backend) as file:
    #                     if tcp_var in file.read():
    #                         print("В skdpu_tcp_var_backend запись найдена...")
    #                     else:
    #                         with open(skdpu_tcp_var_backend, 'a') as file:
    #                             templates = yaml.safe_load(tcp_var)
    #                             file.write('  ')
    #                             yaml.dump(templates, file, sort_keys=False, indent=4)
    #                             print("В skdpu_tcp_var_backend запись не найдена, добавляю...")
    #
    #
    def consul(self, config, domain):
        """Сохраняем конфиг в consul"""
    #     config = self.config
        env = config['environment']
        print(env)
        dc = config['dc']
        print(dc)
        c = consul.Consul(host='skdpu-nginxp01.passport.local', port=8500, token='4290d995-ad54-b863-8634-6bfd0337a9c7')
        # c = consul.Consul(host='skdpu-nginxp10.passport.local', port=8500, token='2b886df6-d0d3-726a-141a-1b568d057aa5')
        key_path = f'nginx/http/sites/'
        config_yaml = yaml.dump(config['site_config'].get(f'{domain}_9443'))
        upstreams = tuple(config.get('upstreams_config'))

        if dc == 'kur':
            c.kv.put(f'{key_path}{env}/{domain}_9443', config_yaml)

        elif dc == 'kor':
            c.kv.put(f'{key_path}{env}_kor/{domain}_9443', config_yaml)
        for records in upstreams:
            # print(config['upstreams_config'][records]['main'])
            c.kv.put(f"nginx/http/upstreams/{records}",
                     yaml.dump(config['upstreams_config'][records]['main']))
            c.kv.put(f"nginx/http/upstreams-config/main/{records}",
                     yaml.dump(config['upstreams_config'][records]['main']))
            c.kv.put(f"nginx/http/upstreams-config/backup/{records}",
                     yaml.dump(config['upstreams_config'][records]['backup']))
        return {"updated": f"{domain}"}



