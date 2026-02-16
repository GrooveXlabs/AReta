# superhuman (Phase 2)

Minimal local execution engine foundation with a FastAPI gateway.

## Prerequisites

- Python 3.11 or newer

## Windows setup

1. Install Python 3.11+ from the official installer.
2. Open **PowerShell** in the repository root.
3. Move into the project folder:

```powershell
cd superhuman
```

## Create and activate a virtualenv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If script execution is blocked, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the local gateway server

```powershell
uvicorn gateway.main:app --host 127.0.0.1 --port 8000 --reload
```

## API endpoints

- `GET /health`
- `POST /jobs` with JSON body:

```json
{ "goal": "text" }
```

- `GET /jobs/{id}`

## Job persistence and audit files

Job data is persisted under repository-level `./data/jobs/`:

- Job JSON: `./data/jobs/<job_id>.json`
- Job audit log: `./data/jobs/<job_id>.log`

Inspect files from the repository root:

```powershell
Get-ChildItem .\data\jobs
Get-Content .\data\jobs\<job_id>.json
Get-Content .\data\jobs\<job_id>.log
```

## Security note

Filesystem operations are intended to be restricted to `./workspace`. A placeholder
sandbox utility lives at `tools/sandbox.py` and should be used by future
file-operation tools.
