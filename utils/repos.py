import os

from utils.launch import git_clone

dir_repos = "repositories"


def download_repos():
    # Repositories we care about
    stable_diffusion_repo = os.environ.get(
        "STABLE_DIFFUSION_REPO", "https://github.com/CompVis/stable-diffusion.git"
    )
    taming_transformers_repo = os.environ.get(
        "TAMING_REANSFORMERS_REPO", "https://github.com/CompVis/taming-transformers.git"
    )
    k_diffusion_repo = os.environ.get(
        "K_DIFFUSION_REPO", "https://github.com/crowsonkb/k-diffusion.git"
    )
    codeformer_repo = os.environ.get(
        "CODEFORMET_REPO", "https://github.com/sczhou/CodeFormer.git"
    )
    blip_repo = os.environ.get("BLIP_REPO", "https://github.com/salesforce/BLIP.git")
    # Required commit hashes to avoid breaking changes
    stable_diffusion_commit_hash = os.environ.get(
        "STABLE_DIFFUSION_COMMIT_HASH", "69ae4b35e0a0f6ee1af8bb9a5d0016ccb27e36dc"
    )
    taming_transformers_commit_hash = os.environ.get(
        "TAMING_TRANSFORMERS_COMMIT_HASH", "24268930bf1dce879235a7fddd0b2355b84d7ea6"
    )
    k_diffusion_commit_hash = os.environ.get(
        "K_DIFFUSION_COMMIT_HASH", "f4e99857772fc3a126ba886aadf795a332774878"
    )
    codeformer_commit_hash = os.environ.get(
        "CODEFORMER_COMMIT_HASH", "c5b4593074ba6214284d6acd5f1719b6c5d739af"
    )
    blip_commit_hash = os.environ.get(
        "BLIP_COMMIT_HASH", "48211a1594f1321b00f14c9f7a5b4813144b2fb9"
    )

    # Do the cloning/downloading of repos if not downloaded already
    git_clone(
        stable_diffusion_repo,
        os.path.join(dir_repos, "stable-diffusion"),
        "Stable Diffusion",
        stable_diffusion_commit_hash,
    )
    git_clone(
        taming_transformers_repo,
        os.path.join(dir_repos, "taming-transformers"),
        "Taming Transformers",
        taming_transformers_commit_hash,
    )
    git_clone(
        k_diffusion_repo,
        os.path.join(dir_repos, "k-diffusion"),
        "K-diffusion",
        k_diffusion_commit_hash,
    )
    git_clone(
        codeformer_repo,
        os.path.join(dir_repos, "CodeFormer"),
        "CodeFormer",
        codeformer_commit_hash,
    )
    git_clone(blip_repo, os.path.join(dir_repos, "BLIP"), "BLIP", blip_commit_hash)
