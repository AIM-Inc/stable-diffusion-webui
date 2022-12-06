import json
import os

from utils.launch import run

extensions_dir = "extensions"
git = os.environ.get("GIT", "git")


def opener(path, flags):
    dir_fd = os.open("extensions/config", os.O_RDONLY)
    return os.open(path, flags, dir_fd=dir_fd)


def download_extensions():
    os.makedirs(extensions_dir, exist_ok=True)

    # Normally, we want to only run this when the dir is empty.  However, we
    # don't always know when a new extension is being added so it's best to
    # stay up-to-date by performing this step all the time.
    if next(os.scandir(extensions_dir), None):
        print("Downloading extensions...")

        stable_diffusion_ext_repo = os.environ.get(
            "STABLE_DIFFUSION_EXT_REPO",
            "https://github.com/AIM-Inc/stable-diffusion-extensions.git",
        )

        # Let's delete the extensions dir before cloning
        run(
            "rm -rf extensions",
            "Deleting extensions dir before cloning",
            "An error occurred while trying to rm extensions/",
        )
        run(
            f'"{git}" clone "{stable_diffusion_ext_repo}" "{extensions_dir}"',
            f"Cloning Stable Diffusion Extensions into {extensions_dir}...",
            "Couldn't clone Stable Diffusion Extensions",
        )
        # Remove .git stuff so it's not treated as a submodule
        run(
            "rm -rf extensions/.git",
            "Removing .git links",
            "Failed to remove .git links",
        )
        run(
            "rm extensions/.gitignore",
            "Removing .gitignore from extensions/",
            "Failed to remove .gitignore from extensions/",
        )

        repos = []

        # Some extensions that are not developed by us have other repos it
        # relies on.  These repos are captured by the config.json file.  So,
        # we need to grab it and parse it to clone repos that are
        # dependencies.
        with open("config.json", opener=opener) as f:
            data = json.load(f)

            for key, value in data.items():
                repos = [*repos, *value["repositories"]]

        for repo in repos:
            git_url = repo["url"]
            repo_path = repo["path"]
            name = repo["name"]

            if not os.path.exists(repo_path):
                run(
                    f'"{git}" clone "{git_url}" "{repo_path}"',
                    f"Cloning {name} into {repo_path}...",
                    f"Couldn't clone {name}",
                )
