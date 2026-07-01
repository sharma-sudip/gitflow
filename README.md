# git-automation

Interactive CLI for the day-to-day git workflow: branch → stage → commit → push.

## Project structure

```
git-automation/
├── gitflow.py          # Main script — interactive git workflow
├── gitflow.bat         # Windows launcher (double-click or run from cmd)
├── requirements.txt    # Python dependencies
└── testxml/            # XML test fixtures (test1.xml … test10.xml)
```

## Requirements

- Python 3.10+
- Git

Install dependencies:

```
pip install -r requirements.txt
```

## Usage

Run from inside any git repository.

**Windows (cmd / PowerShell):**
```
gitflow.bat
```

**Any platform:**
```
python gitflow.py
```

You will be prompted to choose a mode:

| Mode | What it does |
|------|-------------|
| **New branch + stage + commit + push** | Creates a new branch off `main`/`master`, then stages, commits, and pushes |
| **Stage + commit + push on current branch** | Skips branch creation and works on the current branch |

## Workflow

### 1. Branch creation (full mode only)

Select a branch type, enter an optional ticket number (prompted for `bugfix` branches), and a short description. The branch is named automatically:

```
bugfix/1234-fix-null-pointer
feature/add-login-page
```

The script fetches and checks out the latest `main`/`master` before creating the branch.

Supported types: `feature`, `bugfix`, `fix`, `hotfix`, `chore`, `docs`, `refactor`

### 2. Staging

An interactive checklist shows all changed files. Use **space** to toggle files and **enter** to confirm.

### 3. Committing

A diff summary is printed before you enter a commit message.

### 4. Pushing

You are asked to confirm before the branch is pushed to `origin` with `--set-upstream`.

## Debugging

A PyCharm remote debugger hook is included but commented out at the top of `gitflow.py`. To use it, uncomment the `pydevd_pycharm.settrace(...)` block and start a PyCharm debug server on port `8062`.
