"""Script for collecting and summarizing GitHub repository information."""

import os
import sys
from dataclasses import dataclass

import pandas as pd
import requests

# === Configuration ===
GITHUB_API_TOKEN = os.environ["GITHUB_API_TOKEN"]
HEADERS = {"Authorization": f"Bearer {GITHUB_API_TOKEN}"}


# === Data structure ===
@dataclass
class Context:
    """Container for user and repository data."""

    user: str
    data: pd.DataFrame


# === Step 1: Fetch repository list ===
def fetch_repo(user: str) -> Context:
    """Fetch all repositories of a user."""
    try:
        url = f"https://api.github.com/users/{user}/repos"
        res = requests.get(url, timeout=10, headers=HEADERS).json()

        df = pd.DataFrame(res)
        df = df.reindex(
            columns=["name", "updated_at", "description", "contributions", "languages"]
        )
        df["languages"] = df["languages"].astype("object")

        print("✅ Repositories fetched successfully\n")
        return Context(user, df)

    except requests.RequestException as e:
        print(f"❌ fetch_repo failed: {e}")
        sys.exit(1)


# === Step 2: Update repository details ===
def update_repo_data(ctx: Context, title: str):
    """Add description, updated_at, languages, and contributions."""
    try:
        # Get detailed repo info
        url = f"https://api.github.com/repos/{ctx.user}/{title}"
        res = requests.get(url, timeout=10, headers=HEADERS)

        if res.status_code != 200:
            print(
                f"⚠️ Skipping {title}: Failed to fetch details (Status: {res.status_code})"
            )
            return

        repo_detail = res.json()

        ctx.data.loc[ctx.data["name"] == title, "updated_at"] = repo_detail.get(
            "updated_at", ""
        )
        ctx.data.loc[ctx.data["name"] == title, "description"] = (
            repo_detail.get("description") or "No Description"
        )

        # Languages
        languages_url = repo_detail.get("languages_url")
        if languages_url:
            res_lang = requests.get(languages_url, timeout=10, headers=HEADERS)
            if res_lang.status_code == 200:
                repo_languages = res_lang.json()
                ctx.data.loc[ctx.data["name"] == title, "languages"] = [repo_languages]
            else:
                print(
                    f"⚠️ Failed to fetch languages for {title} (Status: {res_lang.status_code})"
                )

        # Contributions (first contributor's commits)
        contributors_url = repo_detail.get("contributors_url")
        if contributors_url:
            res_contrib = requests.get(contributors_url, timeout=10, headers=HEADERS)
            if res_contrib.status_code == 200:
                repo_contributors = res_contrib.json()
                if isinstance(repo_contributors, list) and repo_contributors:
                    ctx.data.loc[ctx.data["name"] == title, "contributions"] = (
                        repo_contributors[0].get("contributions", 0)
                    )
                else:
                    ctx.data.loc[ctx.data["name"] == title, "contributions"] = 0
            else:
                print(
                    f"⚠️ Failed to fetch contributors for {title} "
                    f"(Status: {res_contrib.status_code})"
                )
                ctx.data.loc[ctx.data["name"] == title, "contributions"] = 0
        else:
            ctx.data.loc[ctx.data["name"] == title, "contributions"] = 0

    except requests.RequestException as e:
        print(f"❌ update_repo_data failed for {title}: {e}")


# === Step 3: Output repository README locally ===
def output_repo_data(ctx: Context, title: str):
    """Fetch README and save it as index.md in /documents."""
    try:
        res = requests.get(
            f"https://api.github.com/repos/{ctx.user}/{title}/readme",
            timeout=10,
            headers=HEADERS,
        ).json()

        if "download_url" not in res:
            print(f"❎ No README found in {title}")
            return

        # Save README
        md_url = res["download_url"]
        md_content = requests.get(md_url, timeout=10).text

        folder_path = f"documents/{title}"
        os.makedirs(folder_path, exist_ok=True)

        with open(os.path.join(folder_path, "index.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
            f.write(
                f"\n\n---\n\n[`Go Back to Top Page`](https://{ctx.user}.github.io/)\n"
            )

        print(f"✅ {title}: index.md created")

    except requests.RequestException as e:
        print(f"❌ output_repo_data failed: {e}")


# === Step 4: Generate summary README ===
def update_summary_data(ctx: Context):
    """Write summary README.md with repo info sorted by contributions."""
    ctx.data = ctx.data.sort_values(by="contributions", ascending=False)

    with open("README.md", "a", encoding="utf-8") as f:
        for _, row in ctx.data.iterrows():
            title = row["name"]
            description = row["description"]
            contributions = row["contributions"]
            updated_at = row["updated_at"]
            languages_dict = row["languages"]

            if isinstance(languages_dict, dict) and languages_dict:
                languages_str = ", ".join(f"`{lang}`" for lang in languages_dict.keys())
            else:
                languages_str = "`None`"

            f.writelines(
                [
                    f"## {title}\n\n",
                    f"> Repo Link : [{title}](https://github.com/{ctx.user}/{title})\n",
                    ">\n",
                    f"> Description : {description}\n",
                    ">\n",
                    f"> Contributions : {contributions}\n",
                    ">\n",
                    f"> Last Updated : {updated_at}\n",
                    ">\n",
                    f"> Languages : {languages_str}\n\n",
                    f"[`Watch Detail`](https://{ctx.user}.github.io/documents/{title}/)\n\n",
                ]
            )

    print("\n✅ Summary README.md updated")


# === Step 5: Main process ===
def main():
    """Main entry point."""
    user = "k4nkan"

    # Create context
    ctx = fetch_repo(user)
    if ctx.data.empty:
        print("No repositories to process.")
        return

    # Fetch details for each repository
    for repo_name in ctx.data["name"]:
        update_repo_data(ctx, repo_name)
        output_repo_data(ctx, repo_name)

    # Generate summary README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# [{user}.github.io](https://{user}.github.io/)\n\n")

    update_summary_data(ctx)


if __name__ == "__main__":
    main()
