#!/bin/bash

pip install flake8
flake8 --ignore=W503,E203
pytest tests/ --cov=repobee_feedback --cov-branch
