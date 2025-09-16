from collections import defaultdict
from dataclasses import dataclass
import datetime


@dataclass
class RepositoryAuthorCommitsNum:
    author: str
    commits_num: int


@dataclass
class Commit:
    author: str
    commit_dt: datetime.datetime


@dataclass
class RepoCommits:
    repo_url: str
    commits: list[Commit]


@dataclass
class RepoInfo:
    repo_url: str
    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str | None = None


@dataclass
class Repository:
    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str
    authors_commits_num_today: list[RepositoryAuthorCommitsNum]

    @classmethod
    def from_repo_and_commits(
        cls,
        repo_info: RepoInfo,
        commits_info: RepoCommits,
    ):
        author_commits_count = defaultdict(lambda: 0)
        for commit in commits_info.commits:
            author_commits_count[commit.author] += 1
        author_commits_num_today: list[RepositoryAuthorCommitsNum] = []
        for author, count in author_commits_count.items():
            author_commits_num_today.append(RepositoryAuthorCommitsNum(author=author, commits_num=count))
        return cls(
            name=repo_info.name,
            owner=repo_info.owner,
            position=repo_info.position,
            stars=repo_info.stars,
            watchers=repo_info.watchers,
            forks=repo_info.forks,
            language=repo_info.language,
            author_commits_num_today=author_commits_num_today,
        )