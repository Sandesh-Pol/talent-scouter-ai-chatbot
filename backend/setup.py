"""
TalentScout Quick Start Script

This script helps you get started with the TalentScout backend quickly.
It checks dependencies, creates .env if needed, runs migrations, and offers
to create a superuser.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num, description):
    """Print formatted step"""
    print(f"\n[{step_num}] {description}")


def run_command(command, description="Running command"):
    """Run a shell command and return success status"""
    print(f"\n  → {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"  ✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is adequate"""
    print_step(1, "Checking Python version")
    
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("  ✗ Python 3.10+ required!")
        return False
    
    print("  ✓ Python version OK")
    return True


def check_venv():
    """Check if in virtual environment"""
    print_step(2, "Checking virtual environment")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("  ✓ Virtual environment active")
        return True
    else:
        print("  ⚠ Virtual environment not detected")
        print("  Recommendation: Activate venv before continuing")
        print("    Windows: .\\venv\\Scripts\\activate")
        print("    macOS/Linux: source venv/bin/activate")
        
        response = input("\n  Continue anyway? (y/N): ")
        return response.lower() == 'y'


def check_env_file():
    """Check if .env file exists, create from template if not"""
    print_step(3, "Checking environment configuration")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("  ✓ .env file exists")
        
        # Check if GROQ_API_KEY is set
        with open(env_path) as f:
            content = f.read()
            if "gsk_your_actual_groq_api_key_here" in content:
                print("\n  ⚠ WARNING: GROQ_API_KEY not configured!")
                print("  Edit .env and add your Groq API key from:")
                print("  https://console.groq.com")
        
        return True
    
    if env_example_path.exists():
        print("  Creating .env from .env.example...")
        import shutil
        shutil.copy(env_example_path, env_path)
        print("  ✓ .env file created")
        print("\n  ⚠ IMPORTANT: Edit .env and add your GROQ_API_KEY!")
        print("  Get your key from: https://console.groq.com")
        return True
    
    print("  ✗ No .env or .env.example found!")
    return False


def install_dependencies():
    """Install Python dependencies"""
    print_step(4, "Installing dependencies")
    
    if not Path("requirements.txt").exists():
        print("  ✗ requirements.txt not found!")
        return False
    
    print("  This may take a few minutes...")
    return run_command(
        "pip install -r requirements.txt",
        "Installing packages"
    )


def run_migrations():
    """Run database migrations"""
    print_step(5, "Running database migrations")
    
    # Make migrations
    if not run_command(
        "python manage.py makemigrations",
        "Creating migrations"
    ):
        return False
    
    # Apply migrations
    if not run_command(
        "python manage.py migrate",
        "Applying migrations"
    ):
        return False
    
    print("  ✓ Database ready")
    return True


def create_superuser():
    """Offer to create superuser"""
    print_step(6, "Creating admin user")
    
    response = input("\n  Create superuser for Django admin? (Y/n): ")
    
    if response.lower() in ['', 'y', 'yes']:
        print("\n  Follow the prompts to create an admin user...\n")
        os.system("python manage.py createsuperuser")
        return True
    
    print("  Skipped. You can create one later with:")
    print("    python manage.py createsuperuser")
    return True


def print_next_steps():
    """Print next steps"""
    print_header("Ready to Go! 🚀")
    
    print("""
Next Steps:

1. Configure your Groq API key:
   • Edit .env and set GROQ_API_KEY
   • Get your key from: https://console.groq.com

2. Start the development server:
   • Run: python manage.py runserver
   • API available at: http://localhost:8000/api/

3. Test the API:
   • Run: python test_api.py
   • Or use the admin: http://localhost:8000/admin/

4. Read the documentation:
   • README.md - Setup and API docs
   • PROJECT_OVERVIEW.md - Architecture deep dive

API Endpoints:
• POST   /api/sessions/start/    - Start new interview
• POST   /api/chat/              - Send messages
• GET    /api/sessions/<id>/     - Get session details
• GET    /api/health/            - Health check

Happy coding! 🎉
""")


def main():
    """Main setup flow"""
    print_header("TalentScout Quick Start")
    print("\nThis script will help you set up the TalentScout backend.")
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Check virtual environment
    if not check_venv():
        sys.exit(1)
    
    # Step 3: Check .env file
    if not check_env_file():
        sys.exit(1)
    
    # Step 4: Install dependencies
    response = input("\n  Install dependencies now? (Y/n): ")
    if response.lower() in ['', 'y', 'yes']:
        if not install_dependencies():
            print("\n  ✗ Failed to install dependencies")
            sys.exit(1)
    else:
        print("  Skipped. Install later with: pip install -r requirements.txt")
    
    # Step 5: Run migrations
    response = input("\n  Run database migrations now? (Y/n): ")
    if response.lower() in ['', 'y', 'yes']:
        if not run_migrations():
            print("\n  ✗ Failed to run migrations")
            sys.exit(1)
    else:
        print("  Skipped. Run later with: python manage.py migrate")
    
    # Step 6: Create superuser
    create_superuser()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
