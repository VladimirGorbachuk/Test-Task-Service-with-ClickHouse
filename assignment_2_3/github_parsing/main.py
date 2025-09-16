import asyncio
import datetime
from logging import basicConfig, getLogger

from github_parsing.entities import Repository
from github_parsing.github_client import github_session, GithubReposScrapper, RpsLimiter
from github_parsing.parse_settings import ParserSettings


basicConfig(level="INFO")
logger = getLogger(__name__)


async def initialize_and_parse() -> list[Repository]:
    settings = ParserSettings.from_env()
    rps_limiter = RpsLimiter(rps=settings.rps)
    async with github_session(
        access_token=settings.token,
        max_connections=settings.max_connections,
    ) as sess:
        scrapper = GithubReposScrapper(
            session=sess,
            rps_limiter=rps_limiter,
        )
        info = await scrapper.get_repositories(commits_since=datetime.datetime.now().date())
        logger.info("collected this info %s", info)
        return info


def main():
    asyncio.run(initialize_and_parse())