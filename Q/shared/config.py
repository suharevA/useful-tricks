# ====================================
# shared/config.py
import logging
import yaml


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


def setup_logging(component_name: str, log_level=logging.INFO):
    """Настройка логирования для компонента"""
    logger = logging.getLogger(component_name)

    if not logger.handlers:  # Избегаем дублирования handlers
        formatter = logging.Formatter(
            f'%(asctime)s - {component_name} - %(levelname)s - %(message)s'
        )

        # Консольный handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Файловый handler
        file_handler = logging.FileHandler(f'logs/{component_name.lower()}.log')
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.setLevel(log_level)

    return logger