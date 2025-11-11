"""
Realtor Directory Automation Setup Script
Installs dependencies and configures the system for automated lead extraction
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str = "") -> bool:
    """Run a command and handle errors."""
    print(f"🔧 {description}")
    try:
        _ = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def setup_virtual_environment() -> bool:
    """Create and activate virtual environment."""
    if not os.path.exists(".venv"):
        print("📦 Creating virtual environment...")
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            return False

    # Activate and upgrade pip
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\python -m pip install --upgrade pip"
    else:  # Linux/Mac
        activate_cmd = ".venv/bin/python -m pip install --upgrade pip"

    return run_command(activate_cmd, "Upgrading pip in virtual environment")


def install_dependencies() -> bool:
    """Install required Python packages."""
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip install -r requirements.txt"
    else:  # Linux/Mac
        pip_cmd = ".venv/bin/pip install -r requirements.txt"

    return run_command(pip_cmd, "Installing Python dependencies")


def create_directories() -> bool:
    """Create required directories."""
    directories = ["outputs", "logs", "config"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

    return True


def create_env_file() -> bool:
    """Create .env file template for configuration."""
    env_content = """# Realtor Directory Automation Configuration
# Copy this file to .env and update with your settings

# Google Sheets Integration (Optional)
# GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/credentials.json
# GOOGLE_SHEETS_DEFAULT_ID=your_sheet_id_here

# Scraping Configuration
DEFAULT_MAX_RECORDS=1000
SCRAPE_DELAY_SECONDS=1

# Scheduling Configuration
WEEKLY_SCRAPE_TIME=08:00
WEEKLY_SCRAPE_DAY=monday

# Output Configuration
OUTPUT_DIRECTORY=outputs
LOG_DIRECTORY=logs
"""

    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        print("📝 Created .env configuration file template")
    else:
        print("📝 .env file already exists")

    return True


def create_task_scheduler_script() -> bool:
    """Create Windows Task Scheduler XML for weekly automation."""
    script_path = os.path.abspath("realtor_automation_scheduler.ps1")
    working_dir = os.path.abspath(".")
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2025-06-30T00:00:00</Date>
    <Author>Realtor Directory Automation</Author>
    <Description>Weekly automated lead extraction from realtor directory</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-07-07T08:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Monday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -File "{script_path}" -Mode once</Arguments>
      <WorkingDirectory>{working_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

    with open("realtor_automation_task.xml", "w") as f:
        f.write(xml_content)

    print("📅 Created Task Scheduler XML file: realtor_automation_task.xml")
    print("   To install: `schtasks /create /xml realtor_automation_task.xml /tn \"Realtor Directory Automation\"`")

    return True
def test_installation() -> bool:
    """Test the installation by running a quick scrape."""
    print("\n🧪 Testing installation...")

    if os.name == 'nt':  # Windows
        python_cmd = ".venv\\Scripts\\python"
    else:  # Linux/Mac
        python_cmd = ".venv/bin/python"

    test_cmd = f'{python_cmd} realtor_automation.py --mode once --max-records 5'

    print("Running test scrape with 5 records...")
    if run_command(test_cmd, "Test scrape"):
        print("✅ Installation test successful!")
        return True
    else:
        print("❌ Installation test failed. Please check the logs.")
        return False
def main() -> bool:
    """Main setup function."""
    print("🏠 Realtor Directory Automation Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return False

    # Setup steps
    setup_steps = [
        ("Virtual Environment", setup_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Directories", create_directories),
        ("Configuration", create_env_file),
        ("Task Scheduler", create_task_scheduler_script)
    ]

    for step_name, step_function in setup_steps:
        print(f"\n📋 Setting up {step_name}...")
        if not step_function():
            print(f"❌ Setup failed at step: {step_name}")
            return False

    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review and update the .env file with your configuration")
    print("2. Run 'RunRealtorAutomation.bat' to start using the system")
    print("3. For weekly automation, import the Task Scheduler XML:")
    print('   `schtasks /create /xml realtor_automation_task.xml /tn "Realtor Directory Automation"`')
    print("\n🧪 Running installation test...")

    # Run test and capture its result
    test_result = test_installation()

    return test_result


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
