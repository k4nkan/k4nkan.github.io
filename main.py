"""script for collect github information"""

import os
import sys
from dataclasses import dataclass

import pandas as pd
import requests

GITHUB_API_TOKEN = os.environ["GITHUB_API_TOKEN"]


@dataclass
class Context:
    """context for saving dataframe"""

    user: str
    data: pd.DataFrame


def fetch_repo(user: str) -> Context:
    """fetch github repos list"""
    try:
        url = f"https://api.github.com/users/{user}/repos"
        res = requests.get(
            url, timeout=10, headers={"Authorization": f"Bearer {GITHUB_API_TOKEN}"}
        ).json()

        result = pd.DataFrame(res)
        result = result.reindex(
            columns=["name", "updated_at", "description", "languages"]
        )

        result["languages"] = result["languages"].astype("object")

        print("✅ / fetch all repo done\n")
        return Context(user, result)

    except Exception as e:
        print(f"fetch_repo failed with {e}")
        sys.exit()


def update_repo_data(ctx: Context, title: str):
    """add description, updated at, languages"""
    try:
        url = f"https://api.github.com/repos/{ctx.user}/{title}"
        repo_detail = requests.get(
            url, timeout=10, headers={"Authorization": f"Bearer {GITHUB_API_TOKEN}"}
        ).json()

        ctx.data.loc[ctx.data["name"] == title, "updated_at"] = repo_detail[
            "updated_at"
        ]
        if repo_detail["description"]:
            ctx.data.loc[ctx.data["name"] == title, "description"] = repo_detail[
                "description"
            ]
        else:
            ctx.data.loc[ctx.data["name"] == title, "description"] = "No Description"

        repo_languages = requests.get(
            url=repo_detail["languages_url"],
            timeout=10,
            headers={"Authorization": f"Bearer {GITHUB_API_TOKEN}"},
        ).json()

        ctx.data.loc[ctx.data["name"] == title, "languages"] = [repo_languages]

    except Exception as e:
        print(f"update_repo failed with {e}")
        sys.exit()


def output_repo_data(ctx: Context, title: str):
    """fetch and update README"""
    try:
        url = f"https://api.github.com/repos/{ctx.user}/{title}/readme"
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
                f.write(f"\n\n[top](https://{ctx.user}.github.io/)\n")

            description = ctx.data.loc[ctx.data["name"] == title, "description"].values[
                0
            ]
            updated_at = ctx.data.loc[ctx.data["name"] == title, "updated_at"].values[0]
            languages_dict = ctx.data.loc[
                ctx.data["name"] == title, "languages"
            ].values[0]

            if isinstance(languages_dict, dict) and languages_dict:
                languages_str = ", ".join(f"`{lang}`" for lang in languages_dict.keys())
            else:
                languages_str = "`None`"

            with open("README.md", "a", encoding="utf-8") as f:
                lines = [
                    f"## {title}\n\n",
                    f"> Repo Link : [{title}](https://github.com/{ctx.user}/{title})\n",
                    ">\n",
                    f"> Description : {description}\n" ">\n",
                    f"> Last Updated : {updated_at}\n",
                    ">\n",
                    f"> Languages : {languages_str}\n\n",
                    f"[`Watch Detail`](https://{ctx.user}.github.io/documents/{title}/)\n\n",
                ]
                f.writelines(lines)

            print(f"✅ / {title}: index.md created and linked")

        else:
            print(f"❎ /  No README found in {title}")

    except Exception as e:
        print(f"output_repo failed with {e}")


def main():
    """main function"""
    user = "k4nkan"

    # create ctx
    ctx = Context(user, pd.DataFrame())

    # read use repo datas and store to cxt
    ctx = fetch_repo(user)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("# [k4nkan.github.io](https://k4nkan.github.io/)\n\n")

    # update ctx and README
    if not ctx.data.empty:
        for repo_name in ctx.data["name"]:
            update_repo_data(ctx, repo_name)
            output_repo_data(ctx, repo_name)


if __name__ == "__main__":
    main()
