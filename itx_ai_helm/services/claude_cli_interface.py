# itx_ai_helm/services/claude_cli_interface.py (Fixed version)

import subprocess
import json
import time
import os
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

_logger = logging.getLogger(__name__)


class ClaudeCliInterface:
    """Singleton interface for Claude CLI"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.workspace_base = Path('/tmp/itx_ai_helm')
            self.workspace_base.mkdir(exist_ok=True)
            self.current_workspace = None

            # Find claude CLI executable
            self.claude_cli_path = self._find_claude_cli()

            # Enable mock mode for testing if CLI not found
            self.mock_mode = False
            if not self.claude_cli_path:
                _logger.warning("Claude CLI not found, enabling mock mode for testing")
                self.mock_mode = True

            self.initialized = True
            _logger.info(f"ClaudeCliInterface initialized with CLI at: {self.claude_cli_path}")
            if self.mock_mode:
                _logger.info("Running in MOCK MODE for testing")

    def _find_claude_cli(self) -> str:
        """Find claude executable"""
        # Try different possible command names and paths
        possible_commands = [
            'claude',  # Standard name
            'claude-code',  # Alternative name
            'claude-cli'  # Another alternative
        ]

        # Common installation paths (including nvm paths)
        possible_paths = [
            os.path.expanduser('~/.nvm/versions/node/v22.19.0/bin/claude'),
            '/home/chainarp/.nvm/versions/node/v22.19.0/bin/claude',  # Direct path from your system
        ]

        # First try the specific paths
        for path in possible_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                _logger.info(f"Found Claude CLI at: {path}")
                return path

        # Then try to find via which command
        for cmd in possible_commands:
            try:
                result = subprocess.run(['which', cmd], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip()
                    _logger.info(f"Found Claude CLI via which: {path}")
                    return path
            except:
                pass

        # Try with full PATH including nvm
        env = os.environ.copy()
        # Add nvm paths to PATH
        nvm_path = os.path.expanduser('~/.nvm/versions/node/')
        if os.path.exists(nvm_path):
            for node_version in os.listdir(nvm_path):
                bin_path = os.path.join(nvm_path, node_version, 'bin')
                if os.path.exists(bin_path):
                    env['PATH'] = f"{bin_path}:{env.get('PATH', '')}"

        for cmd in possible_commands:
            try:
                result = subprocess.run(['which', cmd], capture_output=True, text=True, env=env)
                if result.returncode == 0 and result.stdout.strip():
                    path = result.stdout.strip()
                    _logger.info(f"Found Claude CLI with extended PATH: {path}")
                    return path
            except:
                pass

        _logger.warning("Claude CLI not found in any location")
        return None

    def execute_command(self, command: str, workspace: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute command using claude CLI

        Args:
            command: The command/prompt to send to Claude
            workspace: Optional workspace directory

        Returns:
            Dict with status, output, errors
        """

        _logger.info("=== EXECUTE COMMAND DEBUG ===")
        _logger.info(f"Command: {command[:100]}...")
        _logger.info(f"CLI Path: {self.claude_cli_path}")
        _logger.info(f"Mock Mode: {self.mock_mode}")

        # MOCK MODE FOR TESTING
        if self.mock_mode or not self.claude_cli_path:
            _logger.info("Using MOCK MODE")
            mock_responses = {
                "สวัสดี": "สวัสดีครับ! ผม Claude AI Assistant ยินดีช่วยเหลือคุณครับ",
                "hello": "Hello! I'm Claude AI Assistant. How can I help you today?",
                "test": "This is a test response from mock mode.",
                "default": f"ได้รับคำสั่งของคุณแล้ว: '{command}'\n\nนี่คือ mock response สำหรับการทดสอบ UI\n\nเมื่อ Claude CLI ทำงานจริง จะตอบกลับข้อความจริงมาที่นี่"
            }

            # Find matching response or use default
            response = mock_responses.get("default")
            for key in mock_responses:
                if key.lower() in command.lower():
                    response = mock_responses[key]
                    break

            # Simulate some code if asked for code
            code_blocks = []
            if "code" in command.lower() or "โค้ด" in command.lower():
                code_blocks = [{
                    'language': 'python',
                    'code': '# Mock code example\ndef hello_world():\n    print("Hello from mock mode!")'
                }]

            return {
                'status': 'success',
                'output': response,
                'errors': '',
                'code_blocks': code_blocks,
                'workspace': str(self.workspace_base),
                'return_code': 0
            }

        # REAL CLI EXECUTION
        try:
            # Set workspace
            if workspace:
                work_dir = self.workspace_base / workspace
            else:
                work_dir = self.workspace_base / f"session_{int(time.time())}"

            work_dir.mkdir(exist_ok=True, parents=True)
            self.current_workspace = work_dir

            # Write command to temp file for complex prompts
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, dir=str(work_dir)) as f:
                f.write(command)
                prompt_file = f.name

            # Execute claude command
            cmd = [self.claude_cli_path, command]

            _logger.info(f"Executing command: {' '.join(cmd[:2])}...")

            # Set up environment with proper PATH
            env = os.environ.copy()
            # Ensure nvm bin is in PATH
            claude_dir = os.path.dirname(self.claude_cli_path)
            if claude_dir and claude_dir not in env.get('PATH', ''):
                env['PATH'] = f"{claude_dir}:{env.get('PATH', '')}"

            _logger.info(f"Working directory: {work_dir}")
            _logger.info("Starting subprocess...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(work_dir),
                timeout=120,  # 2 minutes timeout
                env=env
            )

            _logger.info(f"Subprocess completed with return code: {result.returncode}")
            _logger.info(f"STDOUT length: {len(result.stdout) if result.stdout else 0}")
            _logger.info(f"STDERR length: {len(result.stderr) if result.stderr else 0}")

            if result.stdout:
                _logger.info(f"STDOUT preview: {result.stdout[:500]}")
            if result.stderr:
                _logger.info(f"STDERR preview: {result.stderr[:500]}")

            # Clean up temp file
            try:
                os.unlink(prompt_file)
            except:
                pass

            # Parse output
            output = result.stdout or ""
            errors = result.stderr or ""

            # If no output but command succeeded, might be an issue
            if result.returncode == 0 and not output:
                _logger.warning("Command succeeded but no output received")
                output = "Command executed but no response received"

            # Check for code blocks in output
            code_blocks = self._extract_code_blocks(output)

            # Save generated files if any
            generated_files = self._detect_generated_files(output)

            response = {
                'status': 'success' if result.returncode == 0 else 'error',
                'output': output if output else (errors if errors else "No output received"),
                'errors': errors,
                'code_blocks': code_blocks,
                'generated_files': generated_files,
                'workspace': str(work_dir),
                'return_code': result.returncode
            }

            _logger.info(f"Returning response with status: {response['status']}")
            return response

        except subprocess.TimeoutExpired:
            _logger.error("Command timed out after 120 seconds")
            return {
                'status': 'error',
                'error': 'Command execution timed out after 120 seconds',
                'output': 'Command timed out'
            }
        except Exception as e:
            _logger.error(f"Error executing command: {e}", exc_info=True)
            import traceback
            return {
                'status': 'error',
                'error': str(e),
                'output': f"Error: {str(e)}",
                'traceback': traceback.format_exc()
            }

    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks from response"""
        import re
        code_blocks = []

        # Pattern for code blocks with language
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        for lang, code in matches:
            code_blocks.append({
                'language': lang or 'text',
                'code': code.strip()
            })

        return code_blocks

    def _detect_generated_files(self, output: str) -> List[str]:
        """Detect files that were generated"""
        import re
        files = []

        # Common patterns for file creation
        patterns = [
            r"Created file: (.*)",
            r"Writing to (.*)",
            r"Generated: (.*)",
            r"File saved: (.*)",
            r"→ (.*\.py)",
            r"→ (.*\.xml)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, output)
            files.extend(matches)

        return list(set(files))  # Remove duplicates

    def generate_odoo_component(self, component_type: str, specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Odoo components using Claude"""

        if component_type == 'model':
            prompt = f"""Create an Odoo 17 model file with:
- Model name: {specs.get('name')}
- Fields: {', '.join(specs.get('fields', []))}
- Description: {specs.get('description')}
Include proper imports, class definition, and field declarations."""

        elif component_type == 'view':
            prompt = f"""Create an Odoo 17 {specs.get('view_type', 'form')} view XML for model {specs.get('model')}:
- Fields: {', '.join(specs.get('fields', []))}
- View type: {specs.get('view_type')}
Include proper XML structure with record tags."""

        elif component_type == 'controller':
            prompt = f"""Create an Odoo 17 HTTP controller with:
- Routes: {', '.join(specs.get('routes', []))}
- Auth type: {specs.get('auth', 'user')}
Include proper imports and route decorators."""

        elif component_type == 'wizard':
            prompt = f"""Create an Odoo 17 TransientModel wizard:
- Name: {specs.get('name')}
- Purpose: {specs.get('purpose')}
Include model, view, and action."""

        else:
            prompt = f"Generate Odoo {component_type} component: {json.dumps(specs, indent=2)}"

        return self.execute_command(prompt)

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            'cli_available': self.claude_cli_path is not None,
            'cli_path': self.claude_cli_path,
            'cli_command': os.path.basename(self.claude_cli_path) if self.claude_cli_path else None,
            'workspace': str(self.current_workspace) if self.current_workspace else None,
            'workspace_base': str(self.workspace_base),
            'mock_mode': self.mock_mode
        }


# Singleton instance getter
def get_claude_cli() -> ClaudeCliInterface:
    """Get the singleton Claude CLI interface"""
    return ClaudeCliInterface()