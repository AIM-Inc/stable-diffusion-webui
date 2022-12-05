import os

from utils.launch import git_clone

extensions_dir = "extensions"


def download_extensions():
    with os.scandir(extensions_dir) as ext:
        if not any((True for _ in ext)):
            print("Downloading extensions...")

            stable_diffusion_ext_repo = os.environ.get(
                "STABLE_DIFFUSION_EXT_REPO",
                "https://github.com/AIM-Inc/stable-diffusion-extensions",
            )
            stable_diffusion_ext_commit_hash = os.environ.get(
                "STABLE_DIFFUSION_EXT_COMMIT_HASH",
                "4d11418048ae8fee439958d5b175061c83ad5792",
            )

            git_clone(
                stable_diffusion_ext_repo,
                os.path.join(extensions_dir),
                "temp",
                stable_diffusion_ext_commit_hash,
            )
