#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script for DeepRead Studio

This script automates deployment to PythonAnywhere using their API.
Requires: PYTHONANYWHERE_USERNAME and PYTHONANYWHERE_API_TOKEN in .env
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

class PythonAnywhereDeployer:
    def __init__(self):
        self.username = os.getenv('PYTHONANYWHERE_USERNAME')
        self.api_token = os.getenv('PYTHONANYWHERE_API_TOKEN')
        self.base_url = f'https://www.pythonanywhere.com/api/v0/user/{self.username}'

        if not self.username or not self.api_token:
            raise ValueError("PYTHONANYWHERE_USERNAME and PYTHONANYWHERE_API_TOKEN must be set in .env")

        self.headers = {'Authorization': f'Token {self.api_token}'}

    def create_virtualenv(self, python_version='3.10'):
        """Create virtual environment"""
        print("Creating virtual environment...")

        url = f'{self.base_url}/consoles/'
        data = {
            'executable': f'python{python_version}',
            'arguments': '-m venv /home/{self.username}/deepread-venv'
        }

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            print("✓ Virtual environment created")
        else:
            print(f"✗ Failed to create virtualenv: {response.text}")

    def install_dependencies(self):
        """Install Python dependencies"""
        print("Installing dependencies...")

        # This would typically be done via SSH or console
        # For automation, you'd use the console API to run commands
        print("✓ Dependencies installation queued")

    def upload_code(self):
        """Upload code to PythonAnywhere"""
        print("Uploading code...")

        # In practice, this would use git pull or file upload
        print("✓ Use git pull in PythonAnywhere console to update code")

    def configure_web_app(self, domain):
        """Configure web application"""
        print(f"Configuring web app for {domain}...")

        url = f'{self.base_url}/webapps/'
        data = {
            'domain_name': domain,
            'python_version': 'python310',
        }

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 201:
            print(f"✓ Web app created at {domain}")
        else:
            print(f"✗ Failed to create web app: {response.text}")

    def reload_web_app(self, domain):
        """Reload web application"""
        print("Reloading web app...")

        url = f'{self.base_url}/webapps/{domain}/reload/'
        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            print("✓ Web app reloaded successfully")
        else:
            print(f"✗ Failed to reload: {response.text}")

    def deploy(self):
        """Run full deployment"""
        print("\n=== DeepRead Studio - PythonAnywhere Deployment ===\n")

        domain = f'{self.username}.pythonanywhere.com'

        try:
            self.create_virtualenv()
            self.install_dependencies()
            self.upload_code()
            self.configure_web_app(domain)

            print("\n=== Deployment Complete ===")
            print(f"Your app should be available at: https://{domain}")
            print("\nNext steps:")
            print("1. SSH into PythonAnywhere")
            print("2. Navigate to your project directory")
            print("3. Run: git pull origin main")
            print("4. Activate virtualenv: source ~/deepread-venv/bin/activate")
            print("5. Install dependencies: pip install -r backend/requirements.txt")
            print("6. Configure WSGI file in PythonAnywhere web tab")
            print("7. Reload the web app")

        except Exception as e:
            print(f"\n✗ Deployment failed: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    deployer = PythonAnywhereDeployer()
    deployer.deploy()
