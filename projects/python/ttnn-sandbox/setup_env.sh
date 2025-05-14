#!/bin/bash

pip install torch==2.2.1 --index-url https://download.pytorch.org/whl/cpu
pip install tiktoken
pip install -r requirements.txt

echo "✅ Successfully installed ttnn library"