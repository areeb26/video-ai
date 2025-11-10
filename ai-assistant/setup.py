"""
Setup script for AI Multitask Assistant
Alternative to setup.sh for Windows users or Python-based setup
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def print_colored(message, color='green'):
    """Print colored output"""
    colors = {
        'green': '\033[0;32m',
        'yellow': '\033[1;33m',
        'red': '\033[0;31m',
        'nc': '\033[0m'
    }
    if platform.system() == 'Windows':
        print(message)  # No colors on Windows cmd
    else:
        print(f"{colors.get(color, colors['nc'])}{message}{colors['nc']}")


def check_python_version():
    """Check if Python version meets requirements"""
    print("Checking Python version...")
    required_version = (3, 10)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        print_colored(
            f"Error: Python {required_version[0]}.{required_version[1]} or higher is required",
            'red'
        )
        print_colored(f"Current version: {current_version[0]}.{current_version[1]}", 'red')
        sys.exit(1)

    print_colored(f"✓ Python {current_version[0]}.{current_version[1]} found", 'green')
    print()


def create_virtual_environment():
    """Create Python virtual environment"""
    print("Creating virtual environment...")
    venv_path = Path("venv")

    if venv_path.exists():
        print_colored("Virtual environment already exists. Skipping...", 'yellow')
    else:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_colored("✓ Virtual environment created", 'green')
    print()


def get_venv_python():
    """Get path to Python in virtual environment"""
    if platform.system() == 'Windows':
        return Path("venv") / "Scripts" / "python.exe"
    else:
        return Path("venv") / "bin" / "python"


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    python_path = get_venv_python()

    # Upgrade pip
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
                   check=True, capture_output=True)

    # Install requirements
    subprocess.run([str(python_path), "-m", "pip", "install", "-r", "requirements.txt"],
                   check=True)

    print_colored("✓ Dependencies installed", 'green')
    print()


def create_directories():
    """Create necessary directories"""
    print("Creating directories...")

    directories = [
        "database",
        "static",
        "templates",
        "n8n_workflows",
        "docs"
    ]

    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)

    # Create workspace directory
    workspace_dir = Path.home() / "ai-assistant-workspace"
    if not workspace_dir.exists():
        workspace_dir.mkdir(parents=True)
        print_colored(f"✓ Workspace directory created at: {workspace_dir}", 'green')
    else:
        print_colored(f"Workspace directory already exists: {workspace_dir}", 'yellow')

    print()
    return workspace_dir


def setup_environment(workspace_dir):
    """Setup environment file"""
    print("Setting up environment configuration...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        if env_example.exists():
            # Copy and update
            content = env_example.read_text()
            content = content.replace(
                "WORKSPACE_DIR=/home/user/ai-assistant-workspace",
                f"WORKSPACE_DIR={workspace_dir}"
            )
            env_file.write_text(content)
            print_colored("✓ Environment file created (.env)", 'green')
            print_colored("⚠ Please edit .env and add your N8N settings if needed", 'yellow')
        else:
            print_colored("Warning: .env.example not found", 'yellow')
    else:
        print_colored(".env file already exists. Skipping...", 'yellow')

    print()


def main():
    """Main setup function"""
    print("🤖 AI Multitask Assistant - Setup Script")
    print("=" * 42)
    print()

    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        workspace_dir = create_directories()
        setup_environment(workspace_dir)

        print()
        print("=" * 42)
        print_colored("✓ Setup completed successfully!", 'green')
        print("=" * 42)
        print()
        print("Next steps:")
        print("1. Edit .env file with your configuration")
        print()
        print("2. Start the assistant:")
        if platform.system() == 'Windows':
            print("   venv\\Scripts\\activate")
            print("   python main.py")
        else:
            print("   source venv/bin/activate")
            print("   python main.py")
        print()
        print("3. Access the web interface at:")
        print("   http://localhost:8001")
        print()
        print("4. API documentation at:")
        print("   http://localhost:8001/docs")
        print()
        print("For N8N integration:")
        print("- Install N8N: npm install -g n8n")
        print("- Start N8N: n8n start")
        print("- Import workflows from: n8n_workflows/")
        print()
        print("Happy automating! 🚀")

    except subprocess.CalledProcessError as e:
        print_colored(f"Error during setup: {e}", 'red')
        sys.exit(1)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", 'red')
        sys.exit(1)


if __name__ == "__main__":
    main()
