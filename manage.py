#!/usr/bin/env python
import os
import sys

os.environ['HTTP_HOST'] = 'localhost:8080'
sys.path.append('./site_packages')
from site_packages import rest_framework
sys.modules['rest_framework'] = rest_framework
reload(sys)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "site_config.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
