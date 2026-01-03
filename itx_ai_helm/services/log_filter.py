# itx_ai_helm/services/log_filter.py
"""
Custom logging filter for terminal routes

ใช้สำหรับลด logs ของ terminal polling requests
"""

import logging


class TerminalLogFilter(logging.Filter):
    """
    Filter ออก terminal polling logs

    การใช้งาน:
    1. Import ใน __init__.py
    2. Apply filter ใน controller
    """

    def filter(self, record):
        """
        Filter log records

        Returns:
            bool: False ถ้าต้องการซ่อน log, True ถ้าต้องการแสดง
        """
        # ซ่อน logs ของ terminal routes
        terminal_routes = ['/terminal/poll', '/terminal/write', '/terminal/resize']

        # เช็คว่า log message มี terminal routes หรือไม่
        if hasattr(record, 'args') and len(record.args) > 0:
            path = str(record.args[0]) if record.args else ''
            for route in terminal_routes:
                if route in path:
                    return False  # ซ่อน log

        return True  # แสดง log


def install_terminal_log_filter():
    """
    ติดตั้ง log filter สำหรับ terminal

    เรียกใน controller __init__ หรือ module initialization
    """
    # Get werkzeug logger
    werkzeug_logger = logging.getLogger('werkzeug')

    # ลบ filter เดิมออก (ถ้ามี)
    for f in werkzeug_logger.filters[:]:
        if isinstance(f, TerminalLogFilter):
            werkzeug_logger.removeFilter(f)

    # เพิ่ม filter ใหม่
    werkzeug_logger.addFilter(TerminalLogFilter())

    logging.info("Terminal log filter installed")
