from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from logging import getLogger
from typing import Literal
from urllib.parse import urljoin
import asyncio
import datetime
import time

from aiohttp import ClientSession, TCPConnector
from pydantic import TypeAdapter

from github_parsing.entities import Commit, Repository, RepositoryAuthorCommitsNum, RepoInfo
from github_parsing.serializers import CommitSerializer, RepositoriesResponseSerializer


logger = getLogger(__name__)

GITHUB_API_BASE_URL = "https://api.github.com"


@asynccontextmanager
async def github_session(access_token: str, max_connections: int = 10) -> AsyncGenerator[ClientSession]:
    connector = TCPConnector(limit=max_connections)
    try:
        session = ClientSession(
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {access_token}",
            },
            connector=connector,
        )
        yield session
    finally:
        await session.close()


class RpsLimiter:
    def __init__(self, rps: int = 10, window_sec: int = 1):
        self._window_sec = window_sec
        self._interval = window_sec / rps
        self._timer = time.monotonic
        self._last_reset: float | None = None

    async def allow_or_wait(self) -> Literal[True]:
        if not self._last_reset:
            self._last_reset = self._timer()
            return True
        delta = self._timer() - self._last_reset
        if delta >= self._interval:
            self._last_reset = self._timer()
            return True
        await asyncio.sleep(delta)


class GithubReposScrapper:
    def __init__(self, session: ClientSession, rps_limiter: RpsLimiter):
        self._session = session
        self._rps_limiter = rps_limiter

    async def _get_top_repositories(
        self, 
        limit: int = 100,
    ) -> list[RepoInfo]:
        await self._rps_limiter.allow_or_wait()
        data = await self._session.get(
            urljoin(GITHUB_API_BASE_URL, "search/repositories"),
            params={"q": "stars:>1", "sort": "stars", "order": "desc", "per_page": limit},
        )
        resp = await data.json()
        logger.info("response from search/repositories %s", resp)
        repository_response = TypeAdapter(RepositoriesResponseSerializer).validate_python(resp)
        return repository_response.to_repo_info_list()

    async def _get_repository_commits(
        self,
        repository_commits_url: str,
        *,
        per_page: int = 50,
        since_dt: datetime.datetime,
    ) -> list[Commit]:
        page = 0
        commits: list[CommitSerializer] = []
        while True:
            await self._rps_limiter.allow_or_wait()
            logger.info("current repo commits url %s", repository_commits_url)
            data = await self._session.get(
                repository_commits_url,
                params={"since":since_dt.isoformat(), "per_page": per_page, "page": page},
            )
            if data:
                resp = await data.json()
                commit_info = TypeAdapter(list[CommitSerializer]).validate_python(resp)
                commits.append(commit_info)
            else:
                return [
                    commit_info.to_commit()
                    for commit_info in commits
                ]
            page += 1

    async def get_repositories(self, commits_since: datetime.datetime, top_n: int = 10) -> list[Repository]:
        repos = await self._get_top_repositories(limit=top_n)
        commit_coroutines = []
        for repo in repos:
            commit_coroutines.append(
                self._get_repository_commits(
                    repository_commits_url=urljoin(repo.repo_url + "/", "commits"),
                    since_dt=commits_since,
                ),
            )
        commits_info = await asyncio.gather(*commit_coroutines)
        return self._collect_data(commits_info=commits_info, repos=repos)

    def _collect_data(self, commits_info: list[list[Commit]], repos: list[RepoInfo]) -> list[Repository]:
        url_to_repo = {repo.repo_url: repo for repo in repos}
        collected_info: list[Repository] = []
        for commits_pack in commits_info:
            if commits_pack:
                url = commits_pack[0].repo_url
                repo_info = url_to_repo.pop(url)
                repository = Repository.from_repo_and_commits(
                    repo_info=repo_info,
                    commits_info=commits_pack,
                )
                collected_info.append(repository)
        for repo_info in url_to_repo.values():
            repository = Repository.from_repo_and_commits(
                repo_info=repo_info,
                commits_info=[],
            )
            collected_info.append(repository)
        return collected_info
            

