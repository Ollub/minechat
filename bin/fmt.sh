#!/bin/bash

ARGS=${1:-.}
echo "Run isort"
isort --recursive minechat
find minechat -name '*.py' -exec add-trailing-comma {} +
echo "Run black"
black minechat
