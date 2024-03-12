import subprocess


def lint() -> None:
    subprocess.run(["ruff", "format", "."])
    subprocess.run(["mypy", "--strict", "."])
