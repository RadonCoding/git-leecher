from os import chmod, remove
from stat import S_IWRITE
from shutil import rmtree
from subprocess import DEVNULL
from time import time
import tempfile
import requests
import subprocess


def del_rw(action, name, exc):
    chmod(name, S_IWRITE)
    remove(name)


def main():
    endpoint = "https://api.github.com/search/repositories?q=is:public&per_page=100"
    response = requests.get(endpoint)
    repositories = response.json()["items"]

    repo_count = len(repositories)

    with open(f"output-{time()}.txt", "w+") as log:
        for i in range(repo_count):
            # Get the URL to the repository
            repo_url = repositories[i]["html_url"]

            prefix = f"[{i + 1}/{repo_count}]"

            print(f"{prefix} Scanning {repo_url}")

            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()

            # Clone the repository to the temporary directory
            git_result = subprocess.run(
                ["git", "clone", repo_url, temp_dir], stdout=DEVNULL, stderr=DEVNULL
            )

            # Check if the git clone was succesful
            if git_result.returncode == 0:
                cmd = ["gitleaks", "detect", "-v"]
                gitleaks_result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=temp_dir
                )
                rmtree(temp_dir, onerror=del_rw)

                output = ""

                if gitleaks_result.stdout:
                    output += f"URL:         {repo_url}\n"
                    output += gitleaks_result.stdout

                    print(output)

                    log.write(output)
                    log.flush()
            else:
                print(f"{prefix} Failed to clone {repo_url}")


if __name__ == "__main__":
    main()
