import subprocess
import os

git = os.environ.get("GIT", "git")


def git_clone(url, dir, name, commithash=None):
    # TODO clone into temporary dir and move if successful

    if os.path.exists(dir):
        if commithash is None:
            return

        current_hash = run(
            f'"{git}" -C {dir} rev-parse HEAD',
            None,
            f"Couldn't determine {name}'s hash: {commithash}",
        ).strip()
        if current_hash == commithash:
            return

        run(
            f'"{git}" -C {dir} fetch',
            f"Fetching updates for {name}...",
            f"Couldn't fetch {name}",
        )
        run(
            f'"{git}" -C {dir} checkout {commithash}',
            f"Checking out commit for {name} with hash: {commithash}...",
            f"Couldn't checkout commit {commithash} for {name}",
        )
        return

    run(
        f'"{git}" clone "{url}" "{dir}"',
        f"Cloning {name} into {dir}...",
        f"Couldn't clone {name}",
    )

    if commithash is not None:
        run(
            f'"{git}" -C {dir} checkout {commithash}',
            None,
            "Couldn't checkout {name}'s hash: {commithash}",
        )


def run(command, desc=None, errdesc=None):
    if desc is not None:
        print(desc)

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )

    if result.returncode != 0:

        message = f"""{errdesc or 'Error running command'}.
Command: {command}
Error code: {result.returncode}
stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout)>0 else '<empty>'}
stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr)>0 else '<empty>'}
"""
        raise RuntimeError(message)

    return result.stdout.decode(encoding="utf8", errors="ignore")


git_clone("https://github.com/isl-org/MiDaS.git", "repositories/midas", "midas")
