# ====================================
# agents/q1_parser.py
import requests
import json
from typing import Optional
from portalFastDjango.Q.shared.models import ParsedRequest
from portalFastDjango.Q.shared.config import setup_logging


class AgentQ1:
    """Q1 - Агент для парсинга запросов клиента"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = setup_logging("Q1")

        # Системный промпт вынесен в отдельный метод для удобства изменения
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Возвращает системный промпт для Q1"""
        return """
        Ты Q1 - продвинутый агент-парсер запросов по управлению nginx конфигурациями.

        Ты понимаешь СЛОЖНЫЕ запросы с множественными действиями и различными уровнями конфигурации.

        СТРУКТУРА NGINX:
        1. Server-level параметры: listen, server_name, client_max_body_size, proxy_connect_timeout, wallarm_mode, access_log, error_log, etc.
        2. Location блоки: location /path/ { параметры внутри location }
        3. Location параметры: proxy_pass, gzip on/off, wallarm_mode, limit_req, proxy_read_timeout, etc.

        ТИПЫ ДЕЙСТВИЙ:
        - "add_location" - добавить новый location блок (требует указания пути и параметров).
        - "remove_location" - удалить весь location блок (требует указания пути).
        - "change_location_params" - изменить/добавить/удалить параметры ВНУТРИ существующего location (требует указания пути и параметров).
        - "change_server_params" - изменить/добавить/удалить server-level параметры (требует указания параметров).
        - "change_upstream" - изменить серверы в апстримах (требует указания имени upstream и серверов).
        - "mixed_changes" - комбинация разных типов изменений в одном запросе (например, изменения на server-level и в location).
        - "report_issue" - сообщение о проблеме или ошибке.
        - "other" - все неконкретные запросы, включая:
          - Запросы, где указан только домен без конкретного действия, локации или параметров (например, "сделайте что-нибудь с доменом www.mos.ru").
          - Запросы без домена, действия, локации или параметров (например, "добавьте что-нибудь").
          - Любые другие запросы, не подпадающие под вышеуказанные типы.
        
        ЗАПРЕЩЕННЫЕ изменения server-level:
        - listen, server_name (критичные для работы)
        ЗАЩИТНЫЕ ПРАВИЛА:
        - НИКОГДА не удаляй location / (корневой location)
        - НИКОГДА не удаляй server_name или listen
        - При удалении location проверяй что это не единственный location
        ПРАВИЛА ПАРСИНГА:
        1. ДОМЕНЫ: Извлекай все домены (с точками: site.ru, api-test.mos.ru, etc.). Если домен не указан, поле "domains" должно быть пустым списком: [].
        2. ЛОКАЦИИ: Извлекай пути /api/, /admin, /auth, /contract/, etc. Если пути не указаны, поле "locations" должно быть пустым: [].
        3. ПАРАМЕТРЫ:
           - Для удаления используй значение "DELETE".
           - Для server-level: {"параметр": "значение_или_DELETE"}.
           - Для location-level: {"location_/path/_параметр": "значение_или_DELETE"} (используй полный префикс с путем).
           - Если параметры не указаны, поле "params" должно быть пустым: {}, за исключением случаев "other" (см. ниже).
        4. UPSTREAMS: Если запрос касается upstream, извлеки имя upstream и список серверов (например, {"main": ["ip1:port", "ip2:port"]}). Если upstream не указан, поле "upstreams" должно быть: {"main": [], "backup": []}.
        5. SCHEDULE: Извлеки время планирования (например, "завтра в 10:00") или null, если не указано.
        6. ПРАВИЛО ДЛЯ "other":
           - Если запрос содержит ТОЛЬКО домен (например, "сделайте что-нибудь с доменом www.mos.ru") и НЕ содержит конкретных действий (add_location, remove_location, change_..., etc.), локаций, параметров или upstream, то:
             - "action": "other"
             - "domains": ["указанный_домен"]
             - "locations": []
             - "upstreams": {"main": [], "backup": []}
             - "params": {"description": "Указан только домен без действия, локации или параметров"}
             - "schedule": null
           - Если запрос не содержит домена, действия, локации или параметров (например, "добавьте что-нибудь"), то:
             - "action": "other"
             - "domains": []
             - "locations": []
             - "upstreams": {"main": [], "backup": []}
             - "params": {"description": "Неконкретный запрос без домена, действия, локации или параметров"}
             - "schedule": null
        7. СТРОГАЯ ПРОВЕРКА: Если запрос не соответствует ни одному из конкретных типов действий (add_location, remove_location, change_..., mixed_changes, report_issue), он ДОЛЖЕН быть классифицирован как "other" с соответствующим описанием в "params".

        Верни ТОЛЬКО JSON без лишнего текста:
        {
          "domains": ["домен1", "домен2"],
          "upstreams": {"main": ["ip1:port", "ip2:port"], "backup": ["ip3:port"]},
          "locations": ["/path1", "/path2"],
          "action": "тип_действия",
          "schedule": "время или null",
          "params": {"параметр1": "значение_или_DELETE", "location_/path1/_параметр2": "значение_или_DELETE"}
        }
        """

    def parse_user_request(self, user_message: str) -> Optional[ParsedRequest]:
        """Парсинг пользовательского запроса"""
        self.logger.info(f"Начинаем парсинг запроса: {user_message[:100]}...")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self._call_llm(messages)
            if not response:
                return None

            parsed_data = self._extract_json_from_response(response)
            if not parsed_data:
                return None

            result = ParsedRequest(
                domains=parsed_data.get('domains', []),
                upstreams=parsed_data.get('upstreams', {"main": [], "backup": []}),
                locations=parsed_data.get('locations', []),
                action=parsed_data.get('action', 'other'),
                schedule=parsed_data.get('schedule'),
                params=parsed_data.get('params', {}),
                raw_message=user_message,
                is_other=(parsed_data.get('action') == 'other')  # 👈 тут выставляем
            )

            if result.is_other:
                self.logger.warning(f"Запрос классифицирован как 'other', не обрабатываем дальше: {user_message}")
                return None  # или верни result, если хочешь логировать отдельно

            self.logger.info(f"Успешно распарсили: action={result.action}, domains={result.domains}")
            return result

        except Exception as e:
            self.logger.error(f"Ошибка парсинга: {e}")
            return None

    def _call_llm(self, messages) -> Optional[str]:
        """Вызов LLM API"""
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                data=json.dumps({
                    "model": "qwen/qwen3-235b-a22b:free",
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 1000
                })
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.logger.error(f"LLM API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Ошибка вызова LLM: {e}")
            return None

    def _extract_json_from_response(self, ai_message: str) -> Optional[dict]:
        """Извлечение JSON из ответа LLM"""
        self.logger.debug(f"Raw LLM response: {ai_message}")

        json_start = ai_message.find('{')
        json_end = ai_message.rfind('}') + 1

        if json_start == -1 or json_end == -1:
            self.logger.error("Не найден JSON в ответе LLM")
            return None

        try:
            json_str = ai_message[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            return None