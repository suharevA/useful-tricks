# ====================================
# utils/upstream_manager.py
import yaml
from typing import Optional, Dict
from portalFastDjango.Q.shared.config import setup_logging

class UpstreamManager:
    """Менеджер для работы с файлом апстримов"""

    def __init__(self, upstream_file_path: str):
        self.upstream_file_path = upstream_file_path
        self.logger = setup_logging("UPSTREAM_MANAGER")

    def find_upstream(self, upstream_name: str) -> Optional[Dict]:
        """Поиск апстрима по имени"""
        try:
            with open(self.upstream_file_path, encoding='utf-8') as f:
                templates = yaml.safe_load(f) or {}

            for section, upstreams in templates.items():
                if isinstance(upstreams, dict) and upstream_name in upstreams:
                    self.logger.debug(f"Найден апстрим {upstream_name} в секции {section}")
                    return {
                        "found": True,
                        "config": upstreams[upstream_name],
                        "section": section
                    }

            self.logger.debug(f"Апстрим {upstream_name} не найден")
            return {"found": False, "config": None, "section": None}

        except Exception as e:
            self.logger.error(f"Ошибка поиска апстрима {upstream_name}: {e}")
            return None
