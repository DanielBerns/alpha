import re
import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def git_execute(args, cwd):
    """Helper to execute git commands safely."""
    try:
        return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: git {' '.join(args)}\nError: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'git' command not found. Please ensure Git is installed.", file=sys.stderr)
        sys.exit(1)

def git_add_and_commit(output_dir: Path) -> None:
    try:
       git_execute(["add", "."], output_dir)
       git_execute(["commit", "-m", "Build static site"], output_dir)
       # git_execute(["push"], output_dir)
    except Exception as e:
        print(f"Error during Git add and commit: {e}")

def git_setup_repo(output_dir: Path):
    """Handles the git repository logic based on the required conditions."""
    git_dir = output_dir / ".git"

    if output_dir.exists():
        if not git_dir.exists():
            # Condition 1: Exists, but not a git repo -> Fail
            print(f"Error: Directory '{output_dir}' exists but is not a Git repository.", file=sys.stderr)
            sys.exit(1)
        else:
            # Condition 3: Exists, is a git repo -> Create/checkout 'dev' branch
            print(f"Existing Git repository found at '{output_dir}'. Switching to 'dev' branch...")
            try:
                # Try to checkout 'dev' if it already exists
                subprocess.run(["git", "checkout", "dev"], cwd=output_dir, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                # If 'dev' doesn't exist, create and checkout 'dev'
                git_execute(["checkout", "-b", "dev"], cwd=output_dir)
    else:
        # Condition 2: Does not exist -> Create, init, and setup 'main' branch
        print(f"Creating directory '{output_dir}' and initializing Git repository on branch 'main'...")
        output_dir.mkdir(parents=True, exist_ok=True)
        # Initialize repo with 'main' as the default branch name
        git_execute(["init", "-b", "main"], cwd=output_dir)
