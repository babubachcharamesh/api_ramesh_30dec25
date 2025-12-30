import subprocess
import sys

def run_git_command(command_list):
    """Runs a git command and checks for errors."""
    try:
        result = subprocess.run(command_list, check=True, text=True, capture_output=False)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing: {' '.join(command_list)}")
        print(e)
        sys.exit(1)

def main():
    # Get commit message from arguments or input
    if len(sys.argv) > 1:
        commit_message = " ".join(sys.argv[1:])
    else:
        try:
            commit_message = input("Enter commit message: ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)

    if not commit_message:
        print("Error: Commit message cannot be empty.")
        sys.exit(1)

    print(f"\n🚀 Starting automated push with message: '{commit_message}'")

    # 1. Git Add
    print("\n[1/3] Staging changes (git add .)...")
    run_git_command(["git", "add", "."])

    # 2. Git Commit
    print("\n[2/3] Committing changes...")
    # we use subprocess.run without check=True first to see if there is anything to commit
    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_message], 
        text=True, 
        capture_output=False
    )
    
    if commit_result.returncode != 0:
        # Check if it was "nothing to commit"
        status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status_result.stdout.strip() and commit_result.returncode == 1:
             print("Nothing to commit. Checking if we need to push existing commits...")
        else:
            # If it failed for other reasons, we might want to stop or proceed depending on logic.
            # Usually returncode 1 from commit means nothing to commit, unless there's a syntax error or hook error.
            print("Commit might have failed or there was nothing to commit.")

    # 3. Git Push
    print("\n[3/3] Pushing to remote (git push)...")
    run_git_command(["git", "push"])

    print("\n✅ Done! Changes pushed successfully.")

if __name__ == "__main__":
    main()
