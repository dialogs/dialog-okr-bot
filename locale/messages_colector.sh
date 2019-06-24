#!/bin/bash
list=$(find ../src -type f \( -name '*.py' \)  -print)
xgettext --language=PYTHON -o gtmhub_bot.pot ../gtmhub_bot.py $list