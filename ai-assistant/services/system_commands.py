"""
System Commands Service
Executes system commands with safety checks
"""
import subprocess
import shlex
from typing import Dict, Any, List
from ..core.config import settings


class SystemCommandsService:
    """Service for executing system commands safely"""

    def __init__(self):
        self.enabled = settings.ENABLE_SYSTEM_COMMANDS
        self.safe_commands = settings.SAFE_COMMANDS
        self.blocked_commands = settings.BLOCKED_COMMANDS

    def _is_command_safe(self, command: str) -> tuple[bool, str]:
        """
        Check if a command is safe to execute

        Args:
            command: The command to check

        Returns:
            Tuple of (is_safe, reason)
        """
        if not self.enabled:
            return False, "System commands are disabled"

        # Check for blocked patterns
        command_lower = command.lower()
        for blocked in self.blocked_commands:
            if blocked.lower() in command_lower:
                return False, f"Blocked pattern detected: {blocked}"

        # Extract base command
        try:
            parts = shlex.split(command)
            if not parts:
                return False, "Empty command"

            base_command = parts[0]

            # Check if base command is in safe list
            if base_command not in self.safe_commands:
                return False, f"Command '{base_command}' not in safe commands list"

            return True, ""

        except ValueError as e:
            return False, f"Invalid command syntax: {str(e)}"

    def execute_command(
        self,
        command: str,
        timeout: int = 30,
        capture_output: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a system command safely

        Args:
            command: The command to execute
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            Execution result
        """
        # Safety check
        is_safe, reason = self._is_command_safe(command)
        if not is_safe:
            return {
                "success": False,
                "error": reason,
                "is_safe": False,
                "was_blocked": True,
                "output": "",
                "return_code": -1
            }

        try:
            # Execute command
            result = subprocess.run(
                shlex.split(command),
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=False
            )

            return {
                "success": result.returncode == 0,
                "is_safe": True,
                "was_blocked": False,
                "output": result.stdout if capture_output else "",
                "error": result.stderr if capture_output and result.returncode != 0 else "",
                "return_code": result.returncode,
                "execution_time": None  # Could be tracked with time.time()
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "is_safe": True,
                "was_blocked": False,
                "output": "",
                "return_code": -1
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Command not found",
                "is_safe": True,
                "was_blocked": False,
                "output": "",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "is_safe": True,
                "was_blocked": False,
                "output": "",
                "return_code": -1
            }

    def get_safe_commands(self) -> List[str]:
        """Get list of safe commands"""
        return self.safe_commands

    def add_safe_command(self, command: str) -> bool:
        """
        Add a command to the safe list (runtime only)

        Args:
            command: Command to add

        Returns:
            Success status
        """
        if command not in self.safe_commands:
            self.safe_commands.append(command)
            return True
        return False

    def remove_safe_command(self, command: str) -> bool:
        """
        Remove a command from the safe list (runtime only)

        Args:
            command: Command to remove

        Returns:
            Success status
        """
        if command in self.safe_commands:
            self.safe_commands.remove(command)
            return True
        return False

    def execute_script(
        self,
        script_path: str,
        args: List[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Execute a script file safely

        Args:
            script_path: Path to the script
            args: Script arguments
            timeout: Maximum execution time

        Returns:
            Execution result
        """
        # Build command
        command_parts = [script_path]
        if args:
            command_parts.extend(args)

        command = " ".join(shlex.quote(part) for part in command_parts)

        # For scripts, we need to allow the interpreter
        # This is a simplified version - you might want to add more validation
        return self.execute_command(command, timeout=timeout)
