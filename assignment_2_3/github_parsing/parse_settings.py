from dataclasses import dataclass
import os

@dataclass
class ParserSettings:
    token: str
    rps: int
    max_connections: int

    @classmethod
    def from_env(cls) -> "ParserSettings":
        return cls(
            token = os.environ["GITHUB_API_TOKEN"],
            rps=int(os.environ.get("GITHUB_API_RPS", 10)),
            max_connections=int(os.environ.get("GITHUB_API_MAX_CONNECTIONS", 10)),
        )
