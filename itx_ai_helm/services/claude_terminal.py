# itx_ai_helm/services/claude_terminal.py

import os
import pty
import select
import subprocess
import termios
import struct
import fcntl
import logging
from threading import Thread

_logger = logging.getLogger(__name__)


class ClaudeTerminal:
    def __init__(self, websocket):
        self.websocket = websocket
        self.fd = None
        self.child_pid = None

    def start(self):
        """Start Claude CLI in PTY"""
        # Create pseudo terminal
        self.child_pid, self.fd = pty.fork()

        if self.child_pid == 0:
            # Child process - run Claude CLI
            os.execvp('claude', ['claude'])
        else:
            # Parent process - handle I/O
            self._set_winsize(24, 80)
            self._start_reading()

    def _start_reading(self):
        """Read from PTY and send to websocket"""
        Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        while True:
            try:
                r, _, _ = select.select([self.fd], [], [], 0.1)
                if r:
                    output = os.read(self.fd, 1024).decode('utf-8', errors='ignore')
                    self.websocket.send(output)
            except:
                break

    def write(self, data):
        """Write to PTY"""
        if self.fd:
            os.write(self.fd, data.encode())

    def resize(self, rows, cols):
        """Handle terminal resize"""
        self._set_winsize(rows, cols)

    def _set_winsize(self, rows, cols):
        """Set terminal window size"""
        if self.fd:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)