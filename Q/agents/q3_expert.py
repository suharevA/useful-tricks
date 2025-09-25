# agents/q3_expert.py
import requests
import json
import yaml
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from portalFastDjango.Q.shared.models import ParsedRequest
from portalFastDjango.Q.shared.config import setup_logging, MyDumper
import os


class ExpertQ3:
    """Q3 - эксперт по YAML Nginx. Вносит изменения и сохраняет их в файлы."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = setup_logging("Q3-EXPERT")

        # Системный промпт вынесен в отдельный метод
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Возвращает системный промпт для Q3"""
        return """
            Ты — эксперт по Nginx-конфигурациям в YAML-представлении для production систем.

            СТРУКТУРА КОНФИГУРАЦИИ:
            каждый сервер описывается в формате:
            имя_сервера_порт:
              - server-level параметры (listen, server_name, proxy_set_header, access_log, wallarm_*, etc)
              - location блоки
              - error_page директивы

            ВАЖНЫЕ ПРАВИЛА ДЛЯ LOCATION:

            1. КАЖДЫЙ location ОБЯЗАТЕЛЬНО должен содержать proxy_pass:
               - Базовый формат: proxy_pass http://upstream_name/path;
               - Для корня (/): proxy_pass http://domain_name/;
               - Для подпутей: proxy_pass http://domain_name_path/path;

            2. ГЕНЕРАЦИЯ ИМЕН АПСТРИМОВ:
               - Домен school.mos.ru + location /api/ → upstream: school_mos_ru_api
               - Домен mos.ru + location /contract/ → upstream: mos_ru_contract  
               - Заменяй точки и дефисы на подчеркивания
               - Убирай слэши из имен апстримов

            3. ПРИМЕРЫ ПРАВИЛЬНЫХ LOCATION:
               - location / { proxy_pass http://school_mos_ru/; }
               - location /api/ { proxy_pass http://school_mos_ru_api/api/; }
               - location /contract/ { proxy_pass http://school_mos_ru_contract/contract/; }
               - location /help/lms/ { proxy_pass http://school_mos_ru_help_lms/help/lms/; }

            4. ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ В LOCATION:
               Можно добавлять после proxy_pass:
               - wallarm_mode off/safe_blocking
               - gzip on/off  
               - limit_req zone=... burst=...
               - rewrite правила
               - proxy_read_timeout
               - proxy_set_header
               - proxy_connect_timeout

            5. СЛОЖНЫЕ LOCATION (как в production):
               - Могут содержать вложенные location внутри
               - Могут содержать if условия
               - Могут содержать регулярные выражения
               - Сохраняй их структуру при модификации

            6. ПОРЯДОК В БЛОКЕ LOCATION:
               - Сначала proxy_pass (ОБЯЗАТЕЛЬНО для новых location!)
               - Потом дополнительные параметры
               - Пример: location /api/ { proxy_pass http://upstream/; gzip off; wallarm_mode off; }

            7. УДАЛЕНИЕ ПАРАМЕТРОВ:
               - Если параметр имеет значение "DELETE" - удаляй его полностью
               - Удаляй всю строку с этим параметром
               - Не оставляй пустых строк
            
            8. ДОСТУП В КМС
               - allow 10.0.0.0/8
               - deny all
            
            9. ЗАПРЕЩЕНО УДАЛЯТЬ server_name listen 9443 ssl proxy_protocol

            ДЕЙСТВИЯ:

            - add_location: Добавить новый location с правильным proxy_pass и доп. параметрами
            - remove_location: Удалить весь блок location полностью  
            - change_location_params: Изменить параметры внутри существующего location
            - change_server_params: Изменить server-level параметры
            - mixed_changes: Комбинация изменений server и location уровней

            ФОРМАТИРОВАНИЕ:
            - Сохраняй точное YAML форматирование как в исходном файле
            - Используй те же отступы и структуру
            - НЕ изменяй существующие блоки если они не касаются задачи

            В ОТВЕТЕ:
            Возвращай ТОЛЬКО обновленный YAML блок сервера, без объяснений!

            ПРИМЕР РАБОТЫ:

            Исходный:
            school.mos.ru_9443:
              - listen 9443 ssl proxy_protocol  
              - server_name school.mos.ru
              - wallarm_mode safe_blocking
              - location / { proxy_pass http://school_mos_ru/; }

            Задача: добавь location /api/ с параметрами gzip off, wallarm_mode off

            Результат:
            school.mos.ru_9443:
              - listen 9443 ssl proxy_protocol  
              - server_name school.mos.ru
              - wallarm_mode safe_blocking
              - location / { proxy_pass http://school_mos_ru/; }
              - location /api/ { proxy_pass http://school_mos_ru_api/api/; gzip off; wallarm_mode off; }
        """

    def apply_changes(self, parsed_request: ParsedRequest, selected_configs: Dict[str, List]) -> Dict[str, Any]:
        """
        Для каждого выбранного конфига:
        - отправляет инструкцию + оригинальный блок в LLM,
        - ожидает чистый YAML блок
        - валидирует и сохраняет новый блок в YAML-файле.
        """
        self.logger.info(f"Q3 начинает применение изменений для {len(selected_configs)} доменов")

        results: Dict[str, Any] = {}
        for domain, configs in selected_configs.items():
            results[domain] = []
            for config in configs:
                self.logger.info(f"Q3: обрабатываем {domain} -> {config['config_key']}")

                result = self._process_single_config(domain, config, parsed_request)
                results[domain].append(result)

        self.logger.info(f"Q3 завершил обработку. Результат: {results}")
        return results

    def _process_single_config(self, domain: str, config: Dict, parsed_request: ParsedRequest) -> Dict[str, Any]:
        """Обработка одной конфигурации"""
        path = config.get("path")
        key = config.get("config_key")
        original_block = config.get("config_block", [])

        self.logger.info(f"Q3: применяем изменение для {domain} -> {path} ({key})")

        try:
            # Формируем исходную конфигурацию в YAML формате
            original_yaml = yaml.dump({key: original_block}, default_flow_style=False,
                                      allow_unicode=True, sort_keys=False)

            # Создаем понятную инструкцию для LLM
            action_description = self._create_action_description(parsed_request)

            user_message = f"""
ИСХОДНАЯ КОНФИГУРАЦИЯ:
{original_yaml}

ЗАДАЧА:
{action_description}

Сгенерируй обновленную конфигурацию с примененными изменениями.
"""

            # Вызываем LLM
            ai_response = self._call_llm(user_message)
            if not ai_response:
                return {"config_key": key, "status": "error", "reason": "LLM не ответил"}

            # Парсим YAML ответ
            new_block = self._parse_llm_response(ai_response, key)
            if not new_block:
                return {"config_key": key, "status": "error", "reason": "Некорректный YAML от LLM"}

            # Сохраняем изменения
            if self._save_yaml_block(path, key, new_block):
                return {"config_key": key, "status": "updated", "file": path}
            else:
                return {"config_key": key, "status": "error", "reason": "Ошибка сохранения файла"}

        except Exception as e:
            self.logger.error(f"Q3 ошибка обработки {domain}: {e}")
            return {"config_key": key, "status": "error", "reason": str(e)}

    def _call_llm(self, user_message: str) -> Optional[str]:
        """Вызов LLM API"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                data=json.dumps({
                    "model": "qwen/qwen3-235b-a22b:free",
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 2000
                })
            )

            if response.status_code == 200:
                result = response.json()
                ai_message = result['choices'][0]['message']['content'].strip()
                self.logger.debug(f"Q3 LLM ответ: {ai_message[:200]}...")
                return ai_message
            else:
                self.logger.error(f"Q3 LLM error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Q3 ошибка вызова LLM: {e}")
            return None

    def _parse_llm_response(self, ai_message: str, expected_key: str) -> Optional[List]:
        """Парсинг YAML ответа от LLM"""
        try:
            parsed_yaml = yaml.safe_load(ai_message)
            if not isinstance(parsed_yaml, dict) or expected_key not in parsed_yaml:
                # Пытаемся найти блок с нужным ключом
                self.logger.warning("Q3: неожиданный формат ответа, ищем нужный блок")
                lines = ai_message.split('\n')
                yaml_start = -1
                for i, line in enumerate(lines):
                    if line.strip().startswith(expected_key + ':'):
                        yaml_start = i
                        break

                if yaml_start >= 0:
                    yaml_block = '\n'.join(lines[yaml_start:])
                    parsed_yaml = yaml.safe_load(yaml_block)

                if not isinstance(parsed_yaml, dict) or expected_key not in parsed_yaml:
                    self.logger.error("Q3: не удалось найти правильный YAML блок")
                    return None

            new_block = parsed_yaml[expected_key]
            if not isinstance(new_block, list):
                self.logger.error(f"Q3: блок конфигурации не является списком: {type(new_block)}")
                return None

            # Валидация YAML
            test_yaml = yaml.dump({expected_key: new_block}, default_flow_style=False,
                                  allow_unicode=True, sort_keys=False)
            test_load = yaml.safe_load(test_yaml)
            if not test_load or expected_key not in test_load:
                self.logger.error("Q3: YAML валидация не прошла")
                return None

            return new_block

        except yaml.YAMLError as e:
            self.logger.error(f"Q3 YAML parse error: {e}")
            return None

    def _create_action_description(self, parsed_request: ParsedRequest) -> str:
        """Создает понятное описание действия для LLM"""

        action = parsed_request.action
        domains = ', '.join(parsed_request.domains)
        locations = ', '.join(parsed_request.locations)

        if action == "add_location":
            params_str = ', '.join([f"{k}={v}" for k, v in
                                    parsed_request.params.items()]) if parsed_request.params else "без доп. параметров"
            return f"Добавить location'ы {locations} для домена {domains} с параметрами: {params_str}"

        elif action == "remove_location":
            return f"Удалить location'ы {locations} для домена {domains}"

        elif action == "change_location_params":
            params_str = ', '.join([f"{k}={v}" for k, v in parsed_request.params.items()])
            return f"Изменить параметры в location'ах {locations}: {params_str}"

        elif action == "change_server_params":
            params_str = ', '.join([f"{k}={v}" for k, v in parsed_request.params.items()])
            return f"Изменить server-level параметры: {params_str}"

        elif action == "mixed_changes":
            description_parts = []

            # Server-level изменения
            server_params = {k: v for k, v in parsed_request.params.items() if not k.startswith('location_')}
            if server_params:
                server_str = ', '.join([f"{k}={v}" for k, v in server_params.items()])
                description_parts.append(f"Изменить server параметры: {server_str}")

            # Location-level изменения
            location_params = {k: v for k, v in parsed_request.params.items() if k.startswith('location_')}
            if location_params:
                for k, v in location_params.items():
                    # Парсим location_/api/_gzip → location=/api/, param=gzip
                    parts = k.replace('location_', '').split('_')
                    if len(parts) >= 2:
                        location = '/' + parts[0] + '/'
                        param = '_'.join(parts[1:])
                        description_parts.append(f"В location {location} изменить {param}={v}")

            return '; '.join(description_parts)

        elif action == "change_upstream":
            main_servers = parsed_request.upstreams.get('main', [])
            backup_servers = parsed_request.upstreams.get('backup', [])
            return f"Изменить апстримы: main={main_servers}, backup={backup_servers}"

        else:
            return f"Выполнить действие {action} для домена {domains}"

    def _save_yaml_block(self, file_path: str, config_key: str, new_block: List[str]) -> bool:
        """Перезаписываем ключ config_key в YAML-файле новым блоком"""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Q3: файл не найден {file_path}")
                return False

            # Создаем бэкап
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Q3: создан бэкап {backup_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}

            data[config_key] = new_block

            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, Dumper=MyDumper, default_flow_style=False,
                          allow_unicode=True, sort_keys=False)

            self.logger.info(f"Q3: файл {file_path} успешно обновлен")
            return True

        except Exception as e:
            self.logger.error(f"Q3 ошибка сохранения {file_path}: {e}")
            return False