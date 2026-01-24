# itx_ai_helm/services/bus_broadcaster.py
# Thread-safe Bus Broadcaster for Terminal Output
# Optimized with batching and rate limiting

import logging
import threading
import time
from collections import defaultdict

_logger = logging.getLogger(__name__)


class TerminalBusBroadcaster:
    """
    Thread-safe broadcaster that sends terminal output via bus.bus

    Optimizations:
    1. Batching - รวม output ของ session เดียวกันแล้วส่งพร้อมกัน
    2. Rate limiting - ส่งไม่เกิน X ครั้งต่อวินาที
    3. Non-blocking - ไม่ block reader thread
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Output buffers per session
        self._buffers = defaultdict(str)
        self._buffer_lock = threading.Lock()

        # Settings
        self._db_name = None
        self._running = False
        self._worker_thread = None
        self._flush_interval = 0.05  # Flush every 50ms (20 times/sec max)

        self._initialized = True
        _logger.info("TerminalBusBroadcaster initialized (optimized)")

    def start(self, db_name):
        """Start the broadcaster worker"""
        if self._running:
            return

        self._db_name = db_name
        self._running = True

        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

        _logger.info(f"TerminalBusBroadcaster started for db: {db_name}")

    def stop(self):
        """Stop the broadcaster worker"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=2)
        _logger.info("TerminalBusBroadcaster stopped")

    def broadcast(self, session_id, output_text):
        """
        Queue output for broadcasting (non-blocking)

        Output is buffered and sent in batches every 50ms
        """
        if not self._running:
            return

        # Add to buffer (non-blocking)
        with self._buffer_lock:
            self._buffers[session_id] += output_text

    def _worker(self):
        """
        Worker thread that flushes buffers periodically
        """
        import odoo
        from odoo.modules.registry import Registry

        _logger.info("Bus broadcaster worker started (batched mode)")

        while self._running:
            try:
                # Wait for flush interval
                time.sleep(self._flush_interval)

                # Get all buffered output
                with self._buffer_lock:
                    if not self._buffers:
                        continue

                    # Copy and clear buffers
                    to_send = dict(self._buffers)
                    self._buffers.clear()

                # Nothing to send
                if not to_send:
                    continue

                # Broadcast all in one DB transaction
                try:
                    registry = Registry(self._db_name)
                    with registry.cursor() as cr:
                        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

                        for session_id, output in to_send.items():
                            if output:  # Skip empty
                                channel = f"terminal_{session_id}"
                                env['bus.bus']._sendone(channel, 'terminal_output', {
                                    'session_id': session_id,
                                    'output': output
                                })

                        cr.commit()

                except Exception as e:
                    _logger.error(f"Bus broadcast error: {e}")

            except Exception as e:
                _logger.error(f"Bus worker error: {e}")

        _logger.info("Bus broadcaster worker stopped")


# Global instance
_broadcaster = None


def get_broadcaster():
    """Get or create the global broadcaster instance"""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = TerminalBusBroadcaster()
    return _broadcaster


def start_broadcaster(db_name):
    """Start the global broadcaster"""
    broadcaster = get_broadcaster()
    broadcaster.start(db_name)
    return broadcaster


def broadcast_terminal_output(session_id, output_text):
    """
    Broadcast terminal output (convenience function)
    """
    broadcaster = get_broadcaster()
    if broadcaster._running:
        broadcaster.broadcast(session_id, output_text)
