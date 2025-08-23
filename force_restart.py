#!/usr/bin/env python
"""
Force production web server restart by creating a trigger file
"""
import os
import sys
from datetime import datetime

# Create restart trigger
restart_time = datetime.now().isoformat()
print(f"=== FORCE RESTART TRIGGER ===")
print(f"Restart requested at: {restart_time}")

# Touch a file that might trigger restart
with open('/tmp/restart_trigger', 'w') as f:
    f.write(f"Restart requested at {restart_time}\n")

print("Restart trigger created")
print("Web server should restart automatically")
