# Installation Guide

## Institutional Quant Platform

---

# Purpose

This guide explains how to install and configure the Institutional Quant Platform for local development, GitHub Codespaces, Docker, and production environments.

---

# System Requirements

## Minimum Requirements

| Component | Requirement |
|------------|-------------|
| Operating System | Windows 11, Ubuntu 22.04+, macOS 13+ |
| Python | 3.12+ |
| RAM | 8 GB |
| CPU | 4 Cores |
| Storage | 10 GB Free Space |
| Git | Latest Version |

---

## Recommended Requirements

| Component | Recommendation |
|------------|---------------|
| RAM | 16 GB+ |
| CPU | 8+ Cores |
| SSD | NVMe SSD |
| Python | 3.12 |
| Docker | Latest |
| VS Code | Latest |

---

# Required Software

Install the following software before beginning.

| Software | Purpose |
|----------|----------|
| Git | Version Control |
| Python 3.12 | Runtime |
| Docker Desktop | Containers |
| VS Code | IDE |
| GitHub CLI | Repository Management |
| Terraform | Infrastructure |
| Helm | Kubernetes |
| kubectl | Kubernetes |

---

# Clone Repository

```bash
git clone https://github.com/sakshinekkala28/Institutional_Quant_Platform.git
```

Move into the repository.

```bash
cd Institutional_Quant_Platform
```

---

# Python Virtual Environment

Create a virtual environment.

Linux/macOS

```bash
python3 -m venv .venv
```

Windows

```powershell
python -m venv .venv
```

---

# Activate Environment

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

---

# Upgrade Pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

---

# Install Dependencies

Runtime dependencies

```bash
pip install -r requirements.txt
```

Development dependencies

```bash
pip install -r requirements-dev.txt
```

---

# Install Project

```bash
pip install -e .
```

---

# Install Git Hooks

```bash
pre-commit install
```

Verify

```bash
pre-commit run --all-files
```

---

# Environment Variables

Copy the example configuration.

```bash
cp .env.example .env
```

Update the required values.

Example

```text
APP_ENV=development

LOG_LEVEL=INFO

DATA_DIRECTORY=data/

DUCKDB_PATH=data/institutional_quant.db
```

---

# Verify Installation

Check the Python version.

```bash
python --version
```

Expected

```text
Python 3.12.x
```

---

# Run Quality Checks

Format code

```bash
make format
```

Lint

```bash
make lint
```

Type checking

```bash
make typecheck
```

Run tests

```bash
make test
```

Coverage

```bash
make coverage
```

Security

```bash
make security
```

---

# Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Open

```text
http://localhost:8501
```

---

# Run API

```bash
uvicorn api.main:app --reload
```

Open

```text
http://localhost:8000
```

API Documentation

```text
http://localhost:8000/docs
```

OpenAPI Specification

```text
http://localhost:8000/openapi.json
```

---

# Docker Installation

Build

```bash
docker build -t institutional-quant-platform .
```

Run

```bash
docker run -p 8501:8501 institutional-quant-platform
```

---

# GitHub Codespaces

The repository includes a fully configured Dev Container.

To start:

1. Open the repository on GitHub.
2. Create a new Codespace.
3. Wait for the environment to initialize.
4. The `post-create.sh` script will automatically install dependencies and configure the environment.

---

# Kubernetes

Validate manifests

```bash
make helm

make terraform
```

Deploy using your preferred environment.

---

# Troubleshooting

## Python Version

```bash
python --version
```

Ensure Python 3.12 or later is installed.

---

## Missing Dependencies

Reinstall dependencies.

```bash
pip install -r requirements.txt

pip install -r requirements-dev.txt
```

---

## Pre-commit Issues

Reinstall hooks.

```bash
pre-commit install

pre-commit run --all-files
```

---

## Docker Issues

Verify Docker is running.

```bash
docker version
```

---

## GitHub Actions

Run the same quality checks locally.

```bash
make ci
```

---

# Next Steps

After installation, continue with:

1. Quick Start Guide
2. Development Guide
3. Configuration Guide
4. Architecture Overview

---

# Related Documents

- Quick Start
- Development Guide
- Configuration Guide
- Architecture Overview
- Repository Structure
- Deployment Guide

---

End of Document