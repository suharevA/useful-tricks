# shared/models.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ParsedRequest:
    """Структура для хранения распарсенного запроса от Q1"""
    domains: List[str]
    upstreams: Dict[str, List[str]]  # {"main": [...], "backup": [...]}
    locations: List[str]
    action: str
    schedule: Optional[str]
    params: Dict[str, str]
    raw_message: str
    is_other: bool = False