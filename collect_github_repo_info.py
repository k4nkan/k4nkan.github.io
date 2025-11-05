"""script for collect github information"""

import os
import requests
import pandas as pd

GITHUB_API_TOKEN = os.environ["GITHUB_API_TOKEN"]


def fetch_repo(user: str) -> pd.DataFrame:
    """fetch github repos list"""
    try:
        url = f"https://api.github.com/users/{user}/repos"
        res = requests.get(
            url, timeout=10, headers={"Authorization": f"Bearer {GITHUB_API_TOKEN}"}
        ).json()
        return pd.DataFrame(res)
    except Exception as e:
        print(f"fetch_repo failed with {e}")
        return pd.DataFrame()


def output_repo(user: str, title: str):
    """fetch and save README for each repo"""
    try:
        url = f"https://api.github.com/repos/{user}/{title}/readme"
        res = requests.get(
            url, timeout=10, headers={"Authorization": f"Bearer {GITHUB_API_TOKEN}"}
        ).json()

        if "download_url" in res:
            md_url = res["download_url"]
            md_content = requests.get(md_url, timeout=10).text

            folder_path = f"documents/{title}"
            os.makedirs(folder_path, exist_ok=True)

            index_path = os.path.join(folder_path, "index.md")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(md_content)
                f.write(f"\n\n[top](https://{user}.github.io/)\n")

            with open("README.md", "a", encoding="utf-8") as f:
                lines = [
                    f"## {title}\n\n",
                    f"Repo Link : [{title}](https://{user}.{title})\n\n",
                    f"Last Updated : yyyy.mm.dd\n\n",
                    f"Languages : `languages1`,`languages2`,`languages3`\n\n",
                    f"### [`Watch Detail`](https://{user}.github.io/documents/{title}/)\n\n",
                ]
                f.writelines(lines)

            print(f"✅ {title}: index.md created and linked")

        else:
            print(f"ℹ️ No README found in {title}")

    except Exception as e:
        print(f"output_repo failed with {e}")


def main():
    """main function"""
    user = "k4nkan"
    repo_data = fetch_repo(user)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# [k4nkan.github.io](https://k4nkan.github.io/)\n\n")

    if not repo_data.empty:
        for title in repo_data["name"]:
            output_repo(user, title)
    else:
        print("No repositories found.")


if __name__ == "__main__":
    main()
