# ====================================
# main.py
import os
from agents.q1_parser import AgentQ1
from agents.q2_searcher import AgentQ2
# from agents.q3_expert import ExpertQ3
from shared.config import setup_logging
from typing import Dict, Any


class NginxOrchestrator:
    """Главный оркестратор системы"""

    def __init__(self, config_folder: str, upstream_file_path: str, api_key: str):
        # Создаем папку для логов
        os.makedirs('logs', exist_ok=True)

        self.logger = setup_logging("ORCHESTRATOR")
        self.logger.info("Инициализация оркестратора")

        # Инициализация агентов
        self.q1 = AgentQ1(api_key)
        self.q2 = AgentQ2(config_folder, upstream_file_path)
        # self.q3 = ExpertQ3(api_key)

        self.user_selections = {}

    def process_request(self, user_message: str) -> Dict[str, Any]:
        """Основной метод обработки запроса"""
        self.logger.info("=" * 50)
        self.logger.info(f"НОВЫЙ ЗАПРОС: {user_message}")
        self.logger.info("=" * 50)

        # Этап 1: Парсинг
        self.logger.info("ЭТАП 1: Парсинг запроса через Q1")
        parsed_request = self.q1.parse_user_request(user_message)
        if not parsed_request:
            self.logger.error("Q1 не смог распарсить запрос")
            return {"error": "Ошибка парсинга запроса", "stage": "Q1"}

        self.logger.info(f"Q1 результат: action={parsed_request.action}, domains={parsed_request.domains}")

        # Этап 2: Поиск
        self.logger.info("ЭТАП 2: Поиск конфигураций через Q2")
        search_result = self.q2.search_configurations(parsed_request)

        # Этап 3: Выбор конфигураций
        self.logger.info("ЭТАП 3: Выбор конфигураций")
        self._select_configurations(search_result)

        if not self.user_selections:
            self.logger.warning("Нет выбранных конфигураций")
            return {
                "parsed_request": self._parsed_request_to_dict(parsed_request),
                "search_result": search_result,
                "stage": "NO_CONFIGS"
            }

        # Этап 4: Применение изменений
        self.logger.info("ЭТАП 4: Применение изменений через Q3")
        apply_results = self.q3.apply_changes(parsed_request, self.user_selections)

        self.logger.info(f"Обработка завершена. Результат: {len(apply_results)} доменов обработано")

        return {
            "parsed_request": self._parsed_request_to_dict(parsed_request),
            "search_result": search_result,
            "apply_results": apply_results,
            "stage": "COMPLETED"
        }

    def interactive_mode(self):
        """Интерактивный режим"""
        self.logger.info("Запуск интерактивного режима")
        print("🤖 Nginx Configuration Manager готов к работе!")
        print("Введите 'exit' для выхода")

        while True:
            try:
                user_input = input("\n👤 Ваш запрос: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nВыход из программы")
                break

            if not user_input or user_input.lower() in ['exit', 'quit', 'выход']:
                print("До свидания!")
                break

            result = self.process_request(user_input)
            self._display_result(result)

    def _select_configurations(self, search_result: Dict[str, Any]):
        """Автоматический выбор конфигураций"""
        self.user_selections = {}
        for domain, configs in search_result.get("domains_found", {}).items():
            self.user_selections[domain] = configs
            if len(configs) == 1:
                self.logger.info(f"Автоматически выбрана единственная конфигурация для {domain}")
            else:
                self.logger.info(f"Выбраны ВСЕ {len(configs)} конфигураций для {domain}")

    def _parsed_request_to_dict(self, parsed_request) -> dict:
        """Конвертация ParsedRequest в словарь"""
        return {
            "domains": parsed_request.domains,
            "action": parsed_request.action,
            "upstreams": parsed_request.upstreams,
            "locations": parsed_request.locations,
            "schedule": parsed_request.schedule,
            "params": parsed_request.params
        }

    def _display_result(self, result: dict):
        """Отображение результата"""
        if result.get("error"):
            print(f"❌ Ошибка: {result['error']}")
            return

        pr = result["parsed_request"]
        print(f"\n📋 Результат:")
        print(f"   Действие: {pr['action']}")
        print(f"   Домены: {pr['domains']}")
        print(f"   Локации: {pr['locations']}")

        sr = result.get("search_result", {})
        print(f"   Найдено конфигураций: {sr.get('summary', {}).get('total_configs', 0)}")

        if result.get("apply_results"):
            print("   Результаты применения:")
            for domain, entries in result["apply_results"].items():
                print(f"     {domain}: {len(entries)} изменений")


if __name__ == "__main__":
    CONFIG_FOLDER = "../mosru_nginx/mos_ru_nginx"
    UPSTREAM_FILE = f"{CONFIG_FOLDER}/skdpu_config/skdpu_http_upstreams.yml"
    API_KEY = "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"

    orchestrator = NginxOrchestrator(CONFIG_FOLDER, UPSTREAM_FILE, API_KEY)
    orchestrator.interactive_mode()