from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from hashlib import md5
from pathlib import Path
from typing import Iterator

import click
import pygit2 as git


@contextmanager
def repository() -> git.Repository:
    path = git.discover_repository(os.getcwd())
    repo = git.Repository(path)
    yield repo
    repo.free()


def get_cache_file(repo: git.Repository) -> Path:
    repo_hash = md5(str(repo.path).encode()).hexdigest()
    return f"git-dashboard-{repo_hash}"


def _current_branch(repo: git.Repository) -> Optional[str]:
    return None if repo.head_is_detached else repo.head.shorthand


def _replace_lines(path: Path, lines: List[str]):
    with path.open("w+") as f:
        f.truncate()
        f.write("\n".join(lines))


def update_current_branch(
    repo: git.Repository, *, cache_dir: Path, branch_count: int
) -> None:
    branch = _current_branch(repo)
    path = cache_dir / get_cache_file(repo)
    old_branches = [line for line in path.read_text().split("\n") if line != branch]
    branches = [branch, *old_branches[: branch_count - 1]]
    _replace_lines(path, branches)
    return branches


@click.command()
@click.option("--cache-dir", default=Path.home() / ".cache", type=Path)
@click.option("--branch-count", default=5, type=int)
def main(cache_dir, branch_count):
    with repository() as repo:
        branches = update_current_branch(
            repo, cache_dir=cache_dir, branch_count=branch_count
        )
        print(branches)


@click.command()
@click.argument("index", type=int)
@click.option("--cache-dir", default=Path.home() / ".cache", type=Path)
@click.option("--branch-count", default=5, type=int)
def checkout(index, cache_dir, branch_count):
    with repository() as repo:
        path = cache_dir / get_cache_file(repo)
        branches = path.read_text().split("\n")
        repo.checkout(repo.branches[branches[index]])


if __name__ == "__main__":
    pass
