#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import os
import sys


if len(sys.argv) == 1:
    sys.argv.append("py2exe")

directory = os.path.dirname(os.path.abspath(__file__))
