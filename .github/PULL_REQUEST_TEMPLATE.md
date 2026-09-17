## Summary of Changes

Provide a clear and concise description of what this pull request introduces or changes.

## Related Issue / Starter Task

Closes # (or relates to starter task, e.g., "Task 1: Implement `taskpulse list` command")

- [ ] Starter Task 1: `taskpulse list`
- [ ] Starter Task 2: `taskpulse complete <id>`
- [ ] Starter Task 3: `taskpulse delete <id>`
- [ ] Starter Task 4: `taskpulse export`
- [ ] Bug fix / Other improvement

## Type of Change

- [ ] `feat`: New feature (non-breaking change which adds functionality)
- [ ] `fix`: Bug fix (non-breaking change which fixes an issue)
- [ ] `test`: Adding or updating unit tests
- [ ] `docs`: Documentation updates
- [ ] `refactor`: Code change that neither fixes a bug nor adds a feature
- [ ] `chore`: Maintenance, CI, or dependency update

## Local Verification Steps

Please describe how you verified these changes locally:
1. Run `pytest`
2. Run `flake8 .`
3. Run CLI command: `taskpulse ...`

## PR Checklist

Before submitting this PR, please confirm the following:
- [ ] My branch is up-to-date with `main` (`git checkout main && git pull && git checkout <branch> && git merge main`).
- [ ] My branch name follows the convention (e.g., `feature/<name>`, `bugfix/<name>`, `docs/<name>`).
- [ ] My commit messages follow Conventional Commits (e.g., `feat: add list subcommand`).
- [ ] I have written clear docstrings and comments for newly added methods.
- [ ] I have added unit tests verifying my changes.
- [ ] All tests pass locally (`pytest`).
- [ ] Code passes linting with flake8 (`flake8 .`).
