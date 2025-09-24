# ====================================
# agents/q2_searcher.py
import os
import re
import yaml
from typing import List, Set, Dict, Any
from portalFastDjango.Q.shared.models import ParsedRequest
from portalFastDjango.Q.shared.config import setup_logging
from portalFastDjango.Q.utils.upstream_manager import UpstreamManager


class AgentQ2:
    """Q2 - Агент для поиска конфигураций"""

    def __init__(self, config_folder: str, upstream_file_path: str):
        self.config_folder = config_folder
        self.upstream_file_path = upstream_file_path
        self.upstream_manager = UpstreamManager(upstream_file_path)
        self.logger = setup_logging("Q2")

        self.folders = [
            'production_sites',
            'production_kor_sites',
            'test_sites',
            'test_kor_sites',
            'stage_sites',
            'stage_kor_sites',
            'production_nag_sites',
            'production_ngate_sites',
            'production_kor_ngate_sites',
            'test_nag_sites',
            'production_moshub_kor_sites',
            'production_metro_kor_sites',
            'production_metro_sites',
            'production_mesh_main_kor_sites'
        ]

    def search_configurations(self, parsed_request: ParsedRequest) -> Dict[str, Any]:
        """Основной метод поиска конфигураций"""
        self.logger.info(f"Ищем конфигурации для доменов: {parsed_request.domains}")

        search_result = self._initialize_search_result(parsed_request)

        if not parsed_request.domains:
            self.logger.warning("Домены не указаны")
            return search_result

        # Поиск основных конфигураций
        self._search_domain_configs(parsed_request, search_result)

        # Поиск информации об апстримах при необходимости
        self._search_upstream_info(parsed_request, search_result)

        self.logger.info(f"Поиск завершен. Найдено {search_result['summary']['total_configs']} конфигураций")
        return search_result

    def _initialize_search_result(self, parsed_request: ParsedRequest) -> Dict[str, Any]:
        """Инициализация результата поиска"""
        from datetime import datetime
        return {
            "timestamp": datetime.now().isoformat(),
            "action": parsed_request.action,
            "domains_requested": parsed_request.domains,
            "domains_found": {},
            "domains_not_found": [],
            "upstreams_info": {},
            "summary": {"total_configs": 0, "single_configs": 0, "multiple_configs": 0}
        }

    def _search_domain_configs(self, parsed_request: ParsedRequest, search_result: Dict[str, Any]):
        """Поиск конфигураций доменов"""
        yaml_files = self._find_yaml_files()
        self.logger.info(f"Найдено {len(yaml_files)} YAML файлов для анализа")

        for domain in parsed_request.domains:
            domain_configs = []

            for yaml_file in yaml_files:
                configs_in_file = self._search_configs_in_file(yaml_file, domain)
                domain_configs.extend(configs_in_file)

            self._process_domain_results(domain, domain_configs, search_result)

    def _search_configs_in_file(self, yaml_file: str, domain: str) -> List[Dict[str, Any]]:
        """Поиск конфигураций в конкретном файле"""
        configs = []
        config_data = self._parse_yaml_config(yaml_file)

        folder = self._get_folder_from_path(yaml_file)
        if not folder:
            return configs

        for config_key, config_block in config_data.items():
            if not isinstance(config_block, list):
                continue

            server_names = self._extract_server_names(config_block)
            if domain in server_names:
                upstreams = self._extract_upstreams_from_config(config_block)

                configs.append({
                    "folder": folder,
                    "config_key": config_key,
                    "path": yaml_file,
                    "upstreams": list(upstreams),
                    "server_names": list(server_names),
                    "config_block": config_block
                })

                self.logger.info(f"Найден конфиг для {domain}: {folder}/{config_key}")

        return configs

    def _find_yaml_files(self) -> List[str]:
        """Поиск всех YAML файлов"""
        yaml_files = []
        for folder in self.folders:
            folder_path = os.path.join(self.config_folder, folder)
            if os.path.exists(folder_path):
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        if file.endswith(('.yml', '.yaml')):
                            yaml_files.append(os.path.join(root, file))
        return yaml_files

    def _parse_yaml_config(self, file_path: str) -> Dict[str, Any]:
        """Парсинг YAML файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            self.logger.error(f"Ошибка чтения YAML {file_path}: {e}")
            return {}

    def _extract_server_names(self, config_block: List[str]) -> Set[str]:
        """Извлечение server_name из блока конфигурации"""
        server_names = set()
        for item in config_block:
            if isinstance(item, str) and item.strip().startswith('server_name'):
                parts = item.strip().split()
                if len(parts) >= 2:
                    for i in range(1, len(parts)):
                        domain = parts[i].strip().rstrip(';')
                        if domain:
                            server_names.add(domain)
        return server_names

    def _extract_upstreams_from_config(self, config_block: List[str]) -> Set[str]:
        """Извлечение upstream из блока конфигурации и логирование сразу"""
        upstreams = set()
        for item in config_block:
            if isinstance(item, str):
                pattern = re.compile(r'proxy_pass\s+https?://([^/\s;]+)')
                matches = pattern.findall(item)
                for match in matches:
                    clean_upstream = re.sub(r'[{};]', '', match.strip())
                    upstreams.add(clean_upstream)
                    # сразу пишем в лог
                    self.logger.info(f"Найден upstream в конфиге: {clean_upstream}")
        return upstreams

    def _get_folder_from_path(self, yaml_file: str) -> str:
        """Определение папки из пути файла"""
        for folder in self.folders:
            if folder in yaml_file:
                return folder
        return None

    def _process_domain_results(self, domain: str, domain_configs: List, search_result: Dict[str, Any]):
        """Обработка результатов поиска для домена"""
        if domain_configs:
            search_result["domains_found"][domain] = domain_configs
            search_result["summary"]["total_configs"] += len(domain_configs)

            if len(domain_configs) == 1:
                search_result["summary"]["single_configs"] += 1
            else:
                search_result["summary"]["multiple_configs"] += 1
        else:
            search_result["domains_not_found"].append(domain)
            self.logger.warning(f"Конфигурация для домена {domain} не найдена")

    # def _search_upstream_info(self, parsed_request: ParsedRequest, search_result: Dict[str, Any]):
    #     """Поиск информации об апстримах при необходимости"""
    #     if parsed_request.action not in ["add_location", "change_upstream"]:
    #         return
    #
    #     target_upstreams = set()
    #     for domain, configs in search_result["domains_found"].items():
    #         for config in configs:
    #             target_upstreams.update(config["upstreams"])
    #
    #     for upstream_name in target_upstreams:
    #         if upstream_name not in search_result["upstreams_info"]:
    #             upstream_info = self.upstream_manager.find_upstream(upstream_name)
    #             search_result["upstreams_info"][upstream_name] = upstream_info or {
    #                 "found": False, "config": None, "section": None
    #             }
    #
    #             status = "найден" if upstream_info and upstream_info.get("found") else "не найден"
    #             self.logger.info(f"Апстрим {upstream_name}: {status}")
