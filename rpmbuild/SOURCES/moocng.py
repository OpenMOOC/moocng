#!/usr/bin/env python
import os
import sys

sys.path.append(0, '/etc/openmooc/')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moocng_cfg")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
