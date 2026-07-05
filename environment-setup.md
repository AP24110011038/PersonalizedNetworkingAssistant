# Task 4: Environment Setup

## Overview

A consistent development environment ensures that every team member can run the project without dependency conflicts. The project uses a Python virtual environment (`venv`) and a `requirements.txt` file to manage dependencies.

---

## Environment Configuration

### Step 1: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 2: Activate the Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

Run Python and import the required packages:

```python
import fastapi
import transformers
import torch
import streamlit
import requests
import pydantic
import pytest
import httpx
```

If no errors occur, the environment has been configured successfully.

---

## Main Dependencies

The project uses the following libraries:

- FastAPI
- Uvicorn
- Streamlit
- Transformers
- Torch
- Requests
- Pydantic
- Pytest
- HTTPX

All package versions are specified in the `requirements.txt` file to ensure reproducibility.

---

## Benefits

- Isolates project dependencies
- Prevents version conflicts
- Ensures reproducible development environments
- Makes project setup simple for all developers
