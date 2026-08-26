import os
import subprocess
import random
import time
from datetime import datetime

# ============================================================
# SECTION 1: CONFIG PARSER
# Reads the .env file and extracts your settings.
# ============================================================

def load_config():
    """Read the .env file and return a dictionary of settings."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    if not os.path.exists(env_path):
        print("ERROR: No .env file found.")
        print("Please create a .env file with your settings.")
        print("You can copy .env.example and fill in your values.")
        exit(1)

    config = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    # Check that required settings are present
    if "GITHUB_TOKEN" not in config or not config["GITHUB_TOKEN"]:
        print("ERROR: GITHUB_TOKEN is missing from your .env file.")
        exit(1)

    if "REPO_PATH" not in config or not config["REPO_PATH"]:
        print("ERROR: REPO_PATH is missing from your .env file.")
        exit(1)

    return config


# ============================================================
# SECTION 2: RANDOMIZER
# Generates how many commits to make and the delay between them.
# ============================================================

def get_commit_count():
    """
    Generate a random number of commits using a normal distribution.
    Mean: 7, clamped between 0 and 15.
    Numbers close to 7 are picked more often than numbers near the edges.
    """
    count = round(random.gauss(7, 3))
    count = max(0, min(15, count))
    return count


def get_random_delay():
    """Return a random delay between 1 and 10 seconds."""
    return random.uniform(1, 10)


# ============================================================
# SECTION 3: LOG FILE MANAGER
# Handles the contributions.log file and monthly resets.
# ============================================================

def get_log_file_path(repo_path):
    """Return the full path to the contributions.log file."""
    return os.path.join(repo_path, "contributions.log")


def reset_log_if_new_month(log_path):
    """
    Check if the log file was last written in a previous month.
    If so, clear it and start fresh.
    """
    if not os.path.exists(log_path):
        return

    last_modified = datetime.fromtimestamp(os.path.getmtime(log_path))
    now = datetime.now()

    if last_modified.month != now.month or last_modified.year != now.year:
        print(f"New month detected. Resetting {os.path.basename(log_path)}.")
        with open(log_path, "w") as f:
            f.write("")


def append_to_log(log_path):
    """Add a timestamped line to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"Contribution: {timestamp}\n")


# ============================================================
# SECTION 4: GIT OPERATIONS
# Runs git commands using subprocess to add, commit, and push.
# ============================================================

def run_git_command(repo_path, command):
    """
    Run a git command inside the target repo.
    Returns True if successful, False if something went wrong.
    """
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Git error: {result.stderr.strip()}")
            return False
        return True
    except FileNotFoundError:
        print("ERROR: Git is not installed or not found in your system PATH.")
        print("Please install git and try again.")
        exit(1)


def set_git_credentials(repo_path, token):
    """
    Configure git to use the personal access token for pushing.
    This sets the remote URL to include the token for HTTPS authentication.
    """
    # Get the current remote URL
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("ERROR: This folder doesn't appear to be a git repo with a remote.")
        print(f"Path: {repo_path}")
        exit(1)

    remote_url = result.stdout.strip()

    # If the URL is already using a token or is SSH, convert to HTTPS with token
    if "github.com" in remote_url:
        # Extract owner/repo from various URL formats
        if remote_url.startswith("git@"):
            # SSH format: git@github.com:owner/repo.git
            repo_info = remote_url.split(":")[-1]
        elif "github.com/" in remote_url:
            # HTTPS format: https://github.com/owner/repo.git
            repo_info = remote_url.split("github.com/")[-1]
        else:
            print(f"ERROR: Unrecognized GitHub URL format: {remote_url}")
            exit(1)

        # Remove .git suffix if present
        repo_info = repo_info.replace(".git", "")

        # Set the new URL with token embedded
        new_url = f"https://{token}@github.com/{repo_info}.git"
        run_git_command(repo_path, ["git", "remote", "set-url", "origin", new_url])


def git_add_commit_push(repo_path, message):
    """Stage the log file, commit with the given message, and push."""
    log_file = "contributions.log"

    if not run_git_command(repo_path, ["git", "add", log_file]):
        return False

    if not run_git_command(repo_path, ["git", "commit", "-m", message]):
        return False

    if not run_git_command(repo_path, ["git", "push"]):
        return False

    return True


# ============================================================
# SECTION 5: MAIN FLOW
# Ties everything together.
# ============================================================

def main():
    print("=" * 50)
    print("  active-github — Daily Contribution Generator")
    print("=" * 50)
    print()

    # Load settings
    config = load_config()
    repo_path = config["REPO_PATH"]
    token = config["GITHUB_TOKEN"]

    # Verify the repo path exists
    if not os.path.isdir(repo_path):
        print(f"ERROR: The repo path does not exist: {repo_path}")
        print("Please check the REPO_PATH in your .env file.")
        exit(1)

    # Set up git credentials
    set_git_credentials(repo_path, token)

    # Get the log file path and handle monthly reset
    log_path = get_log_file_path(repo_path)
    reset_log_if_new_month(log_path)

    # Determine how many commits to make today
    commit_count = get_commit_count()
    print(f"Commits planned for today: {commit_count}")
    print()

    if commit_count == 0:
        print("Zero commits today — taking a rest day!")
        return

    # Make the commits
    successful = 0
    for i in range(commit_count):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Auto-commit {timestamp}"

        print(f"  [{i + 1}/{commit_count}] Committing: {message}")

        # Append to the log file
        append_to_log(log_path)

        # Commit and push
        if git_add_commit_push(repo_path, message):
            successful += 1
        else:
            print(f"  Commit {i + 1} failed. Stopping to avoid further errors.")
            break

        # Wait a random delay before the next commit (skip delay after the last one)
        if i < commit_count - 1:
            delay = get_random_delay()
            print(f"  Waiting {delay:.1f} seconds...")
            time.sleep(delay)

    print()
    print(f"Done! {successful}/{commit_count} commits completed successfully.")


# This ensures main() only runs when you execute the file directly,
# not when it's imported by another script.
if __name__ == "__main__":
    main()
