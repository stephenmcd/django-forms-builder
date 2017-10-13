#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals

import sys
import os

from settings import PROJECT_ROOT, PROJECT_DIRNAME

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.abspath(os.path.join(PROJECT_ROOT, "..")))

if __name__ == "__main__":
    settings_module = "%s.settings" % PROJECT_DIRNAME
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
