# active-github

A simple Python script that commits timestamped entries to a log file in any repo you point it at, with a random number of commits each day to simulate natural activity.

---

## How It Works

When you run `main.py`, the script:

1. Reads your GitHub token and target repo path from a `.env` file
2. Generates a random number of commits (0–15) using a normal distribution centered around 7
3. For each commit, appends a timestamped line to `contributions.log` in the target repo
4. Commits and pushes each change with a timestamped commit message (e.g., `Auto-commit 2026-08-25 14:32:07`)
5. Waits a random 1–10 second delay between commits so timestamps look natural

The log file resets automatically at the start of each new month.

---

## Prerequisites

- Python 3.8 or higher
- Git installed and available in your terminal
- A GitHub account
- A GitHub Personal Access Token with `repo` scope (Instructions later in the README)

---

## Setup

### Option A: Interactive Setup (Recommended for Beginners)

1. Clone this repo:
   ```
   git clone https://github.com/YOUR_USERNAME/active-github.git
   cd active-github
   ```

2. Run the setup script:
   ```
   python setup.py
   ```

3. Follow the prompts — it will ask for your GitHub token and repo path, validate both, and create your `.env` file.

### Option B: Manual Setup

1. Clone this repo:
   ```
   git clone https://github.com/YOUR_USERNAME/active-github.git
   cd active-github
   ```

2. Copy the example environment file:
   ```
   cp .env.example .env
   ```

3. Open `.env` in any text editor and fill in your values:
   ```
   GITHUB_TOKEN=your_personal_access_token
   REPO_PATH=/full/path/to/your/target/repo
   ```

### Generating a Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Give it a name (e.g., `active-github`)
4. Set an expiration (90 days is a good starting point)
5. Check only the **repo** scope
6. Click **Generate token** and copy it immediately — GitHub only shows it once

---

## Usage

Run the script manually whenever you want to add contributions:

```
python main.py
```

You'll see output like:

```
==================================================
  active-github — Daily Contribution Generator
==================================================

Commits planned for today: 8

  [1/8] Committing: Auto-commit 2026-08-25 14:32:07
  Waiting 4.2 seconds...
  [2/8] Committing: Auto-commit 2026-08-25 14:32:11
  Waiting 7.8 seconds...
  ...

Done! 8/8 commits completed successfully.
```

---

## Project Structure

```
active-github/
├── main.py          # Main script — run this daily
├── setup.py         # Interactive setup wizard
├── .env             # Your settings (not tracked by git)
├── .env.example     # Template showing required settings
├── .gitignore       # Keeps .env out of version control
└── README.md        # This file
```

---

## Troubleshooting

**"No .env file found"** — You haven't created your `.env` file yet. Run `python setup.py` or copy `.env.example` to `.env` and fill in your values.

**"GITHUB_TOKEN is missing"** — Your `.env` file exists but doesn't have a `GITHUB_TOKEN` line, or the value is blank.

**"Token is invalid or expired"** — Generate a new token at https://github.com/settings/tokens and update your `.env` file.

**"The repo path does not exist"** — The `REPO_PATH` in your `.env` doesn't point to a real folder. Check for typos and make sure you're using the full absolute path.

**"This folder is not a git repository"** — The folder exists but isn't a git repo. Make sure you cloned it with `git clone` or initialized it with `git init`.

**"Git is not installed"** — Install git from https://git-scm.com/downloads
