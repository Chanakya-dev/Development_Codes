import os
import subprocess

# Define the repository URL
REPO_URL = "https://github.com/AcademiXedu-DSA/TestRepo3.git"

# Clone the repository
def clone_repo():
    subprocess.run(["git", "clone", REPO_URL])
    repo_name = REPO_URL.split("/")[-1].replace(".git", "")
    os.chdir(repo_name)  # Navigate into the cloned repository directory
    return repo_name

# List all branches, excluding the main branch
def get_branches():
    branches = subprocess.check_output(["git", "branch", "-r"]).decode("utf-8").splitlines()
    return [branch.strip().split('/')[-1] for branch in branches if "origin/" in branch and "main" not in branch]

# Clear all files in the current branch
def clear_branch_data():
    for file in os.listdir("."):
        if file not in [".git"]:  # Exclude .git folder
            if os.path.isdir(file):
                subprocess.run(["rm", "-rf", file])
            else:
                os.remove(file)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Clear branch data"])

# Merge the main branch into the current branch
def merge_main():
    # Fetch and reset branch to match the main branch's state exactly
    subprocess.run(["git", "fetch", "origin"])
    subprocess.run(["git", "reset", "--hard", "origin/main"])  # Force reset to match main exactly

# Push changes to the remote branch
def push_changes(branch):
    subprocess.run(["git", "push", "-f", "origin", branch])  # Force push to overwrite with main's state

# Main script to clear and merge
def clear_and_merge():
    # Clone the repository and navigate to it
    clone_repo()
    
    # Ensure on main branch first
    subprocess.run(["git", "checkout", "main"])
    subprocess.run(["git", "pull", "origin", "main"])  # Pull latest from main
    
    branches = get_branches()

    for branch in branches:
        # Checkout each branch
        subprocess.run(["git", "checkout", branch])

        # Pull the latest for the branch
        subprocess.run(["git", "pull", "origin", branch])

        # Clear branch data
        clear_branch_data()

        # Merge main into the branch
        merge_main()

        # Push updated branch data to GitHub
        push_changes(branch)

    # Return to the main branch
    subprocess.run(["git", "checkout", "main"])

if __name__ == "__main__":
    clear_and_merge()
