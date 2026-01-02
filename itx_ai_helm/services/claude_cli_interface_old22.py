# itx_ai_helm/services/claude_cli_interface.py (Updated version)

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
    """Singleton interface for Claude Code CLI"""

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
            self.initialized = True
            _logger.info("ClaudeCliInterface initialized")

    def execute_command(self, command: str, workspace: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute command using claude-code CLI

        Args:
            command: The command/prompt to send to Claude
            workspace: Optional workspace directory

        Returns:
            Dict with status, output, errors
        """
        try:
            # Set workspace
            if workspace:
                work_dir = self.workspace_base / workspace
            else:
                work_dir = self.workspace_base / f"session_{int(time.time())}"

            work_dir.mkdir(exist_ok=True, parents=True)
            self.current_workspace = work_dir

            # Write command to temp file (for complex prompts)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(command)
                prompt_file = f.name

            # Execute claude-code command
            # Using direct command execution (not interactive mode)
            cmd = ['claude-code', command]

            _logger.info(f"Executing: claude-code with prompt: {command[:100]}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(work_dir),
                timeout=120  # 2 minutes timeout
            )

            # Clean up temp file
            try:
                os.unlink(prompt_file)
            except:
                pass

            # Parse output
            output = result.stdout
            errors = result.stderr

            # Check for code blocks in output
            code_blocks = self._extract_code_blocks(output)

            # Save generated files if any
            generated_files = self._detect_generated_files(output)

            return {
                'status': 'success' if result.returncode == 0 else 'error',
                'output': output,
                'errors': errors,
                'code_blocks': code_blocks,
                'generated_files': generated_files,
                'workspace': str(work_dir),
                'return_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            _logger.error("Command timed out")
            return {
                'status': 'error',
                'error': 'Command execution timed out after 120 seconds'
            }
        except Exception as e:
            _logger.error(f"Error executing command: {e}")
            return {
                'status': 'error',
                'error': str(e)
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

    def create_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Create a file with specific content"""
        prompt = f"""Create a file at {filepath} with this exact content:

{content}

Save the file and confirm creation."""

        return self.execute_command(prompt)

    def analyze_code(self, filepath: str) -> Dict[str, Any]:
        """Analyze existing code file"""

        # Read file content first
        full_path = self.current_workspace / filepath if self.current_workspace else Path(filepath)

        if not full_path.exists():
            return {
                'status': 'error',
                'error': f'File not found: {filepath}'
            }

        prompt = f"""Analyze this Odoo code file at {filepath} and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Performance improvements
4. Best practices violations
5. Suggestions for improvement"""

        return self.execute_command(prompt)

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        # Check if claude-code is available
        try:
            result = subprocess.run(
                ['which', 'claude-code'],
                capture_output=True,
                text=True
            )
            cli_available = result.returncode == 0
            cli_path = result.stdout.strip() if cli_available else None
        except:
            cli_available = False
            cli_path = None

        return {
            'cli_available': cli_available,
            'cli_path': cli_path,
            'workspace': str(self.current_workspace) if self.current_workspace else None,
            'workspace_base': str(self.workspace_base)
        }


# Singleton instance getter
def get_claude_cli() -> ClaudeCliInterface:
    """Get the singleton Claude CLI interface"""
    return ClaudeCliInterface()