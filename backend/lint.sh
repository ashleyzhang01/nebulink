#!/bin/bash
flake8 .
ruff check .
mypy .