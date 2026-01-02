# itx_ai_helm/services/claude_cli_interface_old1.py

import subprocess
import threading
import queue
import json
import time
import os
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

_logger = logging.getLogger(__name__)


class ClaudeCliInterface:
    """Singleton interface for Claude Code CLI"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.process = None
            self.output_queue = queue.Queue()
            self.error_queue = queue.Queue()
            self.is_running = False
            self.reader_thread = None
            self.error_thread = None
            self.workspace_base = Path('/tmp/itx_ai_helm')
            self.workspace_base.mkdir(exist_ok=True)
            self.initialized = True
            _logger.info("ClaudeCliInterface initialized")

    def start_cli(self, workspace: Optional[str] = None) -> bool:
        """Start Claude Code CLI process"""
        if self.is_running and self.process and self.process.poll() is None:
            _logger.info("Claude CLI already running")
            return True

        try:
            # Set workspace
            if workspace:
                work_dir = self.workspace_base / workspace
            else:
                work_dir = self.workspace_base / f"session_{int(time.time())}"

            work_dir.mkdir(exist_ok=True, parents=True)

            # Start Claude Code CLI process
            self.process = subprocess.Popen(
                ['claude-code'],  # Adjust path if needed
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=str(work_dir),
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )

            self.is_running = True

            # Start reader threads
            self.reader_thread = threading.Thread(
                target=self._read_output,
                daemon=True
            )
            self.error_thread = threading.Thread(
                target=self._read_errors,
                daemon=True
            )

            self.reader_thread.start()
            self.error_thread.start()

            _logger.info(f"Claude CLI started in {work_dir}")
            return True

        except FileNotFoundError:
            _logger.error("claude-code command not found. Please install Claude Code CLI")
            return False
        except Exception as e:
            _logger.error(f"Failed to start Claude CLI: {e}")
            return False

    def _read_output(self):
        """Read stdout from CLI process"""
        while self.is_running:
            try:
                if self.process and self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        self.output_queue.put(line.rstrip())
            except Exception as e:
                _logger.error(f"Error reading stdout: {e}")
                break

    def _read_errors(self):
        """Read stderr from CLI process"""
        while self.is_running:
            try:
                if self.process and self.process.stderr:
                    line = self.process.stderr.readline()
                    if line:
                        self.error_queue.put(line.rstrip())
            except Exception as e:
                _logger.error(f"Error reading stderr: {e}")
                break

    def send_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Send command to Claude CLI and get response

        Args:
            command: The command/prompt to send
            timeout: Maximum time to wait for response

        Returns:
            Dict with status, output, errors
        """
        if not self.is_running:
            if not self.start_cli():
                return {
                    'status': 'error',
                    'error': 'Failed to start Claude CLI'
                }

        try:
            # Clear queues
            while not self.output_queue.empty():
                self.output_queue.get_nowait()
            while not self.error_queue.empty():
                self.error_queue.get_nowait()

            # Send command
            if self.process and self.process.stdin:
                self.process.stdin.write(command + '\n')
                self.process.stdin.flush()
                _logger.debug(f"Sent command: {command[:100]}...")
            else:
                return {
                    'status': 'error',
                    'error': 'CLI process not available'
                }

            # Collect response
            output_lines = []
            error_lines = []
            start_time = time.time()
            last_output_time = start_time

            while (time.time() - start_time) < timeout:
                # Check for output
                try:
                    line = self.output_queue.get(timeout=0.1)
                    output_lines.append(line)
                    last_output_time = time.time()
                except queue.Empty:
                    pass

                # Check for errors
                try:
                    error = self.error_queue.get_nowait()
                    error_lines.append(error)
                except queue.Empty:
                    pass

                # Check if response seems complete (no output for 2 seconds)
                if output_lines and (time.time() - last_output_time) > 2:
                    break

            # Parse response
            full_output = '\n'.join(output_lines)
            full_errors = '\n'.join(error_lines)

            # Extract code blocks if present
            code_blocks = self._extract_code_blocks(full_output)

            return {
                'status': 'success',
                'output': full_output,
                'errors': full_errors,
                'code_blocks': code_blocks,
                'execution_time': time.time() - start_time
            }

        except Exception as e:
            _logger.error(f"Error sending command: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks from response"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        for lang, code in matches:
            code_blocks.append({
                'language': lang or 'text',
                'code': code.strip()
            })

        return code_blocks

    def execute_file_operation(self, operation: str, filepath: str, content: str = None) -> Dict[str, Any]:
        """
        Execute file operations through Claude CLI

        Args:
            operation: 'create', 'edit', 'analyze'
            filepath: Path to the file
            content: File content for create/edit operations
        """
        if operation == 'create':
            command = f"Create a file at {filepath} with the following content:\n{content}"
        elif operation == 'edit':
            command = f"Edit the file at {filepath} and update it with:\n{content}"
        elif operation == 'analyze':
            command = f"Analyze the code in {filepath} and suggest improvements"
        else:
            return {'status': 'error', 'error': f'Unknown operation: {operation}'}

        return self.send_command(command)

    def generate_odoo_component(self, component_type: str, specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Odoo components using Claude

        Args:
            component_type: 'model', 'view', 'controller', 'wizard'
            specs: Component specifications
        """
        if component_type == 'model':
            command = f"""Create an Odoo model with these specifications:
            - Name: {specs.get('name')}
            - Fields: {specs.get('fields')}
            - Description: {specs.get('description')}
            Include proper security rules and access rights."""

        elif component_type == 'view':
            command = f"""Create an Odoo {specs.get('view_type', 'form')} view for model {specs.get('model')}:
            - Fields to display: {specs.get('fields')}
            - Include proper groups and attrs
            Generate complete XML view definition."""

        elif component_type == 'controller':
            command = f"""Create an Odoo HTTP controller:
            - Routes: {specs.get('routes')}
            - Authentication: {specs.get('auth', 'user')}
            - Methods: {specs.get('methods')}"""

        else:
            command = f"Generate Odoo {component_type}: {json.dumps(specs)}"

        return self.send_command(command, timeout=60)

    def stop_cli(self):
        """Stop Claude CLI process"""
        self.is_running = False

        if self.process:
            try:
                # Try graceful shutdown
                if self.process.stdin:
                    self.process.stdin.write("exit\n")
                    self.process.stdin.flush()
                    self.process.wait(timeout=5)
            except:
                # Force kill if needed
                self.process.terminate()
                time.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()

            self.process = None
            _logger.info("Claude CLI stopped")

    def restart_cli(self) -> bool:
        """Restart Claude CLI process"""
        self.stop_cli()
        time.sleep(1)
        return self.start_cli()

    def get_status(self) -> Dict[str, Any]:
        """Get current CLI status"""
        is_alive = self.process and self.process.poll() is None

        return {
            'running': self.is_running and is_alive,
            'pid': self.process.pid if self.process else None,
            'workspace': str(self.workspace_base)
        }


# Singleton instance getter
def get_claude_cli() -> ClaudeCliInterface:
    """Get or create the singleton Claude CLI interface"""
    return ClaudeCliInterface()