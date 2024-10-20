#!/bin/bash
flake8 . --fix
ruff check . --fix
mypy .