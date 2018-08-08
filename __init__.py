#!/usr/bin/env python
#  -*- coding:utf-8 -*-

import os
import sys
from setuptools import setup


if len(sys.argv) == 1:
    sys.argv.append("py2exe")

directory = os.path.dirname(os.path.abspath(__file__))

setup(
    zipfile = None,  # 不生成library.zip文件
    windows = [
        {
            "script": directory + "\\interface_multiple.py"
            #"icon_resources":[(1, directory+"\\masterball.ico")]
        }
    ],
)
