import os
import subprocess
import urllib.request
import json

# ============================================================
# SECTION 1: VALIDATE GITHUB TOKEN
# Makes a test API call to GitHub to check the token works.
# ============================================================

def validate_token(token):
    """
    Call the GitHub API to verify the token is valid.
    Returns the GitHub username if successful, None if not.
    """
    try:
        request = urllib.request.Request(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode())
        return data.get("login")
    except urllib.error.HTTPError:
        return None
    except urllib.error.URLError:
        print("ERROR: Could not connect to GitHub.")
        print("Please check your internet connection and try again.")
        return None


# ============================================================
# SECTION 2: VALIDATE REPO PATH
# Checks that the path exists and is a git repo with a remote.
# ============================================================

def validate_repo_path(repo_path):
    """
    Check that the given path is a valid git repo with a GitHub remote.
    Returns True if valid, False if not.
    """
    # Check the folder exists
    if not os.path.isdir(repo_path):
        print(f"ERROR: Folder not found: {repo_path}")
        return False

    # Check it's a git repo
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.isdir(git_dir):
        print("ERROR: This folder is not a git repository.")
        print("Make sure you've run 'git init' or cloned a repo here.")
        return False

    # Check it has a remote
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("ERROR: This repo has no remote named 'origin'.")
        print("Add one with: git remote add origin https://github.com/YOU/REPO.git")
        return False

    remote_url = result.stdout.strip()
    if "github.com" not in remote_url:
        print(f"WARNING: The remote URL doesn't look like a GitHub repo: {remote_url}")
        print("This script is designed for GitHub repositories.")
        return False

    print(f"Repo verified: {remote_url}")
    return True


# ============================================================
# SECTION 3: CREATE .ENV FILE
# Writes the validated settings to a .env file.
# ============================================================

def create_env_file(token, repo_path):
    """Create the .env file with the user's settings."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

    # Warn if .env already exists
    if os.path.exists(env_path):
        overwrite = input("A .env file already exists. Overwrite it? (y/n): ").strip().lower()
        if overwrite != "y":
            print("Setup cancelled. Your existing .env file was not changed.")
            return False

    with open(env_path, "w") as f:
        f.write(f"GITHUB_TOKEN={token}\n")
        f.write(f"REPO_PATH={repo_path}\n")

    print(".env file created successfully.")
    return True


# ============================================================
# SECTION 4: MAIN SETUP FLOW
# Walks the user through setup step by step.
# ============================================================

def main():
    print("=" * 50)
    print("  active-github — Setup")
    print("=" * 50)
    print()
    print("This will walk you through setting up your .env file.")
    print("You'll need your GitHub Personal Access Token and the")
    print("local path to the repo you want to contribute to.")
    print()

    # Step 1: Get and validate the token
    print("STEP 1: GitHub Personal Access Token")
    print("Generate one at: https://github.com/settings/tokens")
    print("Required scope: 'repo'")
    print()

    token = input("Paste your token here: ").strip()

    if not token:
        print("ERROR: No token entered. Exiting.")
        exit(1)

    print("Validating token with GitHub...")
    username = validate_token(token)

    if username:
        print(f"Token is valid! Authenticated as: {username}")
    else:
        print("ERROR: Token is invalid or expired.")
        print("Please generate a new token and try again.")
        exit(1)

    print()

    # Step 2: Get and validate the repo path
    print("STEP 2: Repository Path")
    print("Enter the full local path to the repo you want to")
    print("add contributions to.")
    print()

    repo_path = input("Repo path: ").strip()

    if not repo_path:
        print("ERROR: No path entered. Exiting.")
        exit(1)

    if not validate_repo_path(repo_path):
        exit(1)

    print()

    # Step 3: Create the .env file
    print("STEP 3: Creating .env file")
    if not create_env_file(token, repo_path):
        exit(1)

    print()
    print("=" * 50)
    print("  Setup complete!")
    print("=" * 50)
    print()
    print(f"  GitHub user:  {username}")
    print(f"  Target repo:  {repo_path}")
    print()
    print("  To run: python main.py")
    print()


if __name__ == "__main__":
    main()
