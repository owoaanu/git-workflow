# Contributing to TaskPulse

Welcome to the TaskPulse project! This repository is designed as a hands-on learning environment for interns and junior developers to practice professional Git workflows, automated testing, and collaborative software engineering.

---

## Table of Contents

1. [Code of Conduct & Collaboration](#code-of-conduct--collaboration)
2. [Git Workflow & Branching Strategy](#git-workflow--branching-strategy)
3. [Commit Message Conventions](#commit-message-conventions)
4. [Step-by-Step Contribution Guide](#step-by-step-contribution-guide)
5. [Coding & Testing Standards](#coding--testing-standards)
6. [Pull Request Process & Code Review](#pull-request-process--code-review)
7. [Starter Tasks for Interns](#starter-tasks-for-interns)

---

## Code of Conduct & Collaboration

- Be respectful, constructive, and helpful in issue discussions and pull request reviews.
- Ask questions early if you encounter blockers—no question is too simple!
- Treat code reviews as collaborative learning opportunities rather than criticism.

---

## Git Workflow & Branching Strategy

We follow a structured **Feature Branch Workflow**:

- The `main` branch is protected and always reflects stable, tested code.
- Never commit directly to `main`.
- Always create a new branch from the latest `main` before starting any work.

### Branch Naming Conventions

Use the following prefixes followed by a short, kebab-case description:

| Branch Type | Format | Example |
| :--- | :--- | :--- |
| **New Features** | `feature/<task-description>` | `feature/list-command` |
| **Bug Fixes** | `bugfix/<issue-description>` | `bugfix/fix-null-description` |
| **Documentation** | `docs/<topic>` | `docs/update-install-guide` |
| **Testing** | `test/<test-scope>` | `test/add-storage-tests` |
| **Refactoring** | `refactor/<target-area>` | `refactor/command-loader` |

---

## Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard. This keeps git history clean, readable, and easy to audit.

### Format

```text
<type>(<scope>): <subject>

[optional body explaining motivation and changes]
```

### Commit Types

- `feat`: A new feature (e.g. `feat(commands): add list subcommand with table output`)
- `fix`: A bug fix (e.g. `fix(storage): handle empty title validation`)
- `test`: Adding or updating test cases (e.g. `test(db): add rollback verification`)
- `docs`: Documentation changes (e.g. `docs: update setup steps in README`)
- `refactor`: Code refactoring without changing functionality (e.g. `refactor(cli): clean up parser builder`)
- `chore`: Build scripts, CI configuration, or dependency updates (e.g. `chore(ci): add Python 3.12 to test matrix`)

### Rules for Commit Messages

1. Use the imperative mood ("add feature", not "added feature" or "adds feature").
2. Do not end the subject line with a period.
3. Keep the subject line under 72 characters.

---

## Step-by-Step Contribution Guide

### 1. Clone the Repository

```bash
git clone https://github.com/owoaanu/git-workflow.git
cd git-workflow
```

### 2. Set Up a Python Virtual Environment

TaskPulse requires **Python 3.9+**.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the Package in Editable Mode with Dev Tools

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
```

Verify that the CLI command works:

```bash
taskpulse --help
taskpulse ping
```

### 4. Create Your Feature Branch

Ensure your local `main` is up-to-date, then branch off:

```bash
git checkout main
git pull origin main
git checkout -b feature/my-new-task
```

### 5. Make Changes & Write Tests

- Write clean, modular Python following the existing architecture.
- Add or update unit tests under the `tests/` directory.

### 6. Run Quality Checks Locally

Before committing, ensure that all linters, formatting, and tests pass:

```bash
# 1. Lint code with flake8
flake8 .

# 2. Check code formatting with black
black --check .

# 3. Format code if black reported changes
black .

# 4. Run test suite with coverage
pytest --cov=taskpulse --cov-report=term-missing
```

### 7. Commit and Push

```bash
git add .
git commit -m "feat(commands): add list subcommand"
git push -u origin feature/my-new-task
```

---

## Coding & Testing Standards

- **Modern SQLAlchemy 2.0 ORM**: Database interactions must strictly follow SQLAlchemy 2.0 syntax (`select(Task)`, `session.scalars()`, `session.get(Task, id)`, `Mapped[...]`, `mapped_column(...)`). Avoid legacy 1.x `session.query()` patterns.
- **Minimal Dependencies**: Aside from `sqlalchemy`, TaskPulse uses Python's standard library (`argparse`, `pathlib`, `typing`) for CLI and system interactions.
- **Code Formatting**: Maximum line length is **88 characters** (enforced by `black` and `flake8`).
- **Docstrings & Types**: Every function and module must have clear docstrings explaining arguments, return types, and exceptions. Use type hints where appropriate.
- **Test Coverage**: We maintain **>80% test coverage**. Any new feature or bug fix must include corresponding tests in `tests/`.

---

## Pull Request Process & Code Review

1. **Open a PR**: Go to GitHub and open a Pull Request from your branch against `main`.
2. **Fill Out PR Template**: Fill out every section of the Pull Request Template (Summary, Related Task, Checklist).
3. **CI Checks**: Ensure all GitHub Actions checks (lint, format, test) pass green.
4. **Request Review**: Tag a mentor or fellow intern for review.
5. **Address Feedback**:
   - Make requested changes on your branch.
   - Commit and push; GitHub will update the PR automatically.
   - Reply to comments once addressed.
6. **Merge**: Once approved and all CI checks pass, your PR will be merged using **Squash and Merge** to keep the history clean.

---

## Starter Tasks for Interns

Pick one of the following starter tasks to practice your Git workflow:

### Starter Task 1: Implement `taskpulse list`

- **Goal**: List all tasks in a readable formatted table or list.
- **Flags**:
  - `--status [todo|in_progress|done]` (filter by status)
  - `--priority [low|medium|high]` (filter by priority)
- **Steps**:
  1. Implement `list_tasks()` in [taskpulse/storage.py](file:///home/edsu-dev/Documents/dev/python/interns_contact/git-workflow/taskpulse/storage.py).
  2. Create a new command file `taskpulse/commands/list.py` with `register_subparser` and `execute`.
  3. Register the module in `COMMAND_MODULES` in [taskpulse/cli.py](file:///home/edsu-dev/Documents/dev/python/interns_contact/git-workflow/taskpulse/cli.py).
  4. Write unit tests in `tests/test_storage.py` and `tests/test_commands.py`.

---

### Starter Task 2: Implement `taskpulse complete <task_id>`

- **Goal**: Mark a specific task as `done`.
- **Steps**:
  1. Implement `update_task_status()` in [taskpulse/storage.py](file:///home/edsu-dev/Documents/dev/python/interns_contact/git-workflow/taskpulse/storage.py).
  2. Create `taskpulse/commands/complete.py` taking a required positional argument `task_id`.
  3. Register the command in `taskpulse/cli.py`.
  4. Return an informative message (e.g. `[SUCCESS] Task #<id> marked as done.`) or an error if the task does not exist.
  5. Add unit tests for successful update and invalid ID cases.

---

### Starter Task 3: Implement `taskpulse delete <task_id>`

- **Goal**: Delete a task by ID from the database.
- **Flags**:
  - `--yes`, `-y` (optional flag to bypass interactive confirmation).
- **Steps**:
  1. Implement `delete_task()` in [taskpulse/storage.py](file:///home/edsu-dev/Documents/dev/python/interns_contact/git-workflow/taskpulse/storage.py).
  2. Create `taskpulse/commands/delete.py`.
  3. Register the command in `taskpulse/cli.py`.
  4. Add unit tests covering successful deletion, nonexistent task handling, and the confirmation flag.

---

### Starter Task 4: Implement `taskpulse export`

- **Goal**: Export all stored tasks to a file or stdout in JSON or CSV format.
- **Flags**:
  - `--format [json|csv]` (default: `json`).
  - `--output <filepath>`, `-o <filepath>` (optional output file path; defaults to stdout).
- **Steps**:
  1. Use `storage.list_tasks()` to retrieve tasks.
  2. Use Python's built-in `json` or `csv` standard library modules to format the records.
  3. Create `taskpulse/commands/export.py` and register it in `taskpulse/cli.py`.
  4. Add unit tests checking JSON and CSV output fidelity.
