"""script for collect github information"""

import os
import requests
import pandas as pd

GITHUB_API_TOKEN = os.environ["GITHUB_API_TOKEN"]

def fetch_repo(user: str) -> pd.DataFrame:
    """fetch github repo"""
    try:
        url = f"https://api.github.com/users/{user}/repos"
        res = requests.get(
            url, timeout=10, headers={"Authorization": f"Bearer {GITHUB_API_TOKEN}"}
        ).json()
        return pd.DataFrame(res)

    except Exception as e:
        print(f"fetch repo failed with {e}")
        return pd.DataFrame()


def output_repo(user: str, title: str):
    """output repo data"""
    try:
        url = f"https://api.github.com/repos/{user}/{title}/readme"
        res = requests.get(
            url, timeout=10, headers={"Authorization": f"Bearer {GITHUB_API_TOKEN}"}
        ).json()

        if "download_url" in res:
            result = requests.get(res["download_url"], timeout=10).text
            file_name = f"{title}.md"
            with open(f"documents/{file_name}", "w", encoding="utf-8") as f:
                f.write(result)
                f.write("[top](https://k4nkan.github.io/)")

            with open("README.md", "a", encoding="utf-8") as f:
                f.write(f"[{title}](https://k4nkan.github.io/ducuments/{title}/)\n\n")

            print(f"update done in {title}")

        else:
            print(f"no README in {title}")

    except Exception as e:
        print(f"output repo failed with {e}")


def main():
    """main func for get github data"""
    user = "k4nkan"

    repo_data = fetch_repo(user)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# k4nkan.github.io\n\n## link\n\n")

    if not repo_data.empty:
        for title in repo_data["name"]:
            output_repo(user, title)


if __name__ == "__main__":
    main()
