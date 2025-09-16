import datetime

from pydantic import BaseModel, Field

from github_parsing.entities import RepoInfo, Commit



class AuthorSerializer(BaseModel):
    name: str
    date: datetime.datetime


class CommitSerializer(BaseModel):
    author: AuthorSerializer

    def to_commit(self) -> Commit:
        return Commit(author=self.author.name, commit_dt=self.author.date)


class Owner(BaseModel):
    login: str


class RepositorySerializer(BaseModel):
    name: str
    owner: Owner
    stargazers_count: int
    watchers_count: int
    forks_count: int
    url: str
    language: str | None = None


class RepositoriesResponseSerializer(BaseModel):
    items: list[RepositorySerializer]

    def to_repo_info_list(self) -> list[RepoInfo]:
        repo_info_list: list[RepoInfo] =[]
        for position, item in enumerate(self.items, 1):
            repo_info_list.append(
                RepoInfo(
                    repo_url=item.url,
                    position=position,
                    name=item.name,
                    owner=item.owner.login,
                    stars=item.stargazers_count,
                    watchers=item.watchers_count,
                    forks=item.forks_count,
                    language=item.language,
                )
            )
        return repo_info_list