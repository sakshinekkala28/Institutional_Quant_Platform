#!/usr/bin/env bash

###############################################################################
# Institutional Quant Platform
# Dev Container Post Creation Script
###############################################################################

set -euo pipefail

###############################################################################
# Colors
###############################################################################

GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

###############################################################################
# Banner
###############################################################################

echo -e "${BLUE}"
echo "=============================================================="
echo "      Institutional Quant Platform Development Setup"
echo "=============================================================="
echo -e "${NC}"

###############################################################################
# Upgrade pip
###############################################################################

echo -e "${GREEN}Updating pip...${NC}"

python -m pip install --upgrade pip setuptools wheel

###############################################################################
# Install Requirements
###############################################################################

if [ -f requirements.txt ]; then
    echo -e "${GREEN}Installing requirements.txt...${NC}"
    pip install -r requirements.txt
fi

if [ -f requirements-dev.txt ]; then
    echo -e "${GREEN}Installing requirements-dev.txt...${NC}"
    pip install -r requirements-dev.txt
fi

###############################################################################
# Install Project
###############################################################################

if [ -f pyproject.toml ]; then
    echo -e "${GREEN}Installing project...${NC}"
    pip install -e .
fi

###############################################################################
# Install Pre-commit Hooks
###############################################################################

if command -v pre-commit >/dev/null 2>&1; then
    echo -e "${GREEN}Installing pre-commit hooks...${NC}"
    pre-commit install
fi

###############################################################################
# Create Required Directories
###############################################################################

mkdir -p \
logs \
artifacts \
reports \
coverage \
output \
cache \
tmp

###############################################################################
# Terraform
###############################################################################

if [ -d infrastructure/terraform ]; then

    echo -e "${GREEN}Initializing Terraform...${NC}"

    cd infrastructure/terraform

    terraform init -backend=false || true

    terraform fmt -recursive || true

    terraform validate || true

    cd - >/dev/null

fi

###############################################################################
# Helm
###############################################################################

if [ -d infrastructure/helm ]; then

    echo -e "${GREEN}Validating Helm Chart...${NC}"

    helm lint infrastructure/helm || true

fi

###############################################################################
# Kubernetes
###############################################################################

if [ -d infrastructure/kubernetes ]; then

    echo -e "${GREEN}Kubernetes manifests detected.${NC}"

fi

###############################################################################
# Python Validation
###############################################################################

echo -e "${GREEN}Checking Python syntax...${NC}"

python -m compileall .

###############################################################################
# Ruff
###############################################################################

if command -v ruff >/dev/null 2>&1; then

    echo -e "${GREEN}Running Ruff...${NC}"

    ruff check . || true

fi

###############################################################################
# Black
###############################################################################

if command -v black >/dev/null 2>&1; then

    echo -e "${GREEN}Checking Black formatting...${NC}"

    black --check . || true

fi

###############################################################################
# MyPy
###############################################################################

if command -v mypy >/dev/null 2>&1; then

    echo -e "${GREEN}Running MyPy...${NC}"

    mypy . || true

fi

###############################################################################
# Tests
###############################################################################

if [ -d tests ]; then

    echo -e "${GREEN}Running Test Suite...${NC}"

    pytest -q || true

fi

###############################################################################
# Git Information
###############################################################################

echo

echo -e "${BLUE}Repository Status${NC}"

git status || true

###############################################################################
# Tool Versions
###############################################################################

echo

echo -e "${BLUE}Installed Tools${NC}"

python --version

pip --version

git --version

docker --version 2>/dev/null || true

terraform version 2>/dev/null || true

helm version 2>/dev/null || true

kubectl version --client 2>/dev/null || true

###############################################################################
# Summary
###############################################################################

echo

echo -e "${GREEN}"
echo "=============================================================="
echo " Development Environment Ready"
echo "=============================================================="
echo -e "${NC}"

echo "Repository      : Institutional Quant Platform"
echo "Python          : $(python --version)"
echo "Working Dir     : $(pwd)"
echo

echo "Recommended Commands"

echo "--------------------------------------------------------------"

echo "pytest"

echo "ruff check ."

echo "black ."

echo "mypy ."

echo "terraform validate"

echo "helm lint infrastructure/helm"

echo

echo "Happy Coding!"