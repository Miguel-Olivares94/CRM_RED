#!/usr/bin/env python3
"""
Deploy files to production server using SSH
Uses SSH to upload files without requiring paramiko
"""
import subprocess
import os
from pathlib import Path

# Configuration
HOST = "200.234.225.27"
USER = "root"
PASSWORD = "Django2026!Cloud#"

# Files to deploy
FILES_TO_DEPLOY = {
    "core/views.py": "/home/crm_deploy/crm_app/crm_starter/core/views.py",
    "core/urls.py": "/home/crm_deploy/crm_app/crm_starter/core/urls.py",
    "core/templates/core/subordinados_management.html": "/home/crm_deploy/crm_app/crm_starter/core/templates/core/subordinados_management.html",
    "core/templates/core/base.html": "/home/crm_deploy/crm_app/crm_starter/core/templates/core/base.html",
}

def deploy_file(local_path, remote_path):
    """Deploy a single file using SSH cat piping"""
    try:
        with open(local_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Create the remote directory if needed
        remote_dir = os.path.dirname(remote_path)
        mkdir_cmd = f"mkdir -p {remote_dir}"
        
        # Use scp command - simpler than cat piping
        cmd = ["scp", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
               local_path, f"{USER}@{HOST}:{remote_path}"]
        
        print(f"Uploading {local_path} to {remote_path}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✓ Deployed successfully")
        else:
            print(f"✗ Error: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error deploying {local_path}: {e}")
        return False

def main():
    os.chdir(Path(__file__).parent)
    
    print("Starting file deployment...\n")
    
    success_count = 0
    for local_file, remote_file in FILES_TO_DEPLOY.items():
        local_path = Path(local_file)
        if not local_path.exists():
            print(f"✗ Local file not found: {local_file}")
            continue
        
        if deploy_file(str(local_path), remote_file):
            success_count += 1
        print()
    
    print(f"✓ Deployment complete: {success_count}/{len(FILES_TO_DEPLOY)} files deployed")
    return success_count == len(FILES_TO_DEPLOY)

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
