import re
from typing import Union, List, Any, Iterator


class ReString(str):
    __module__ = "nekobendUtils"

    def __new__(cls, value: str) -> "ReString":
        return super().__new__(cls, value)  # type: ignore

    def __str__(self) -> str:
        return self

    def __repr__(self) -> str:
        return f"ReString('{self}')"

    def to_string(self) -> str:
        return str(self)

    def match(self, pattern: str, string: str, flags=0) -> Union[re.Match[str], None]:
        return re.match(pattern, string, flags)

    def fullmatch(
        self, pattern: str, string: str, flags=0
    ) -> Union[re.Match[str], None]:
        return re.fullmatch(pattern, string, flags)

    def search(self, pattern: str, string: str, flags=0) -> Union[re.Match[str], None]:
        return re.search(pattern, string, flags)

    def sub(
        self, pattern: str, repl: str, string: str, count: int = 0, flags=0
    ) -> "ReString":
        result = re.sub(pattern, repl, string, count, flags)
        return ReString(result)

    def subn(
        self, pattern: str, repl: str, string: str, count: int = 0, flags=0
    ) -> tuple["ReString", int]:
        result, num_subs = re.subn(pattern, repl, string, count, flags)
        return ReString(result), num_subs

    def resplit(
        self, pattern: str, string: str, maxsplit: int = 0, flags=0
    ) -> List[Union["ReString", Any]]:
        results = re.split(pattern, string, maxsplit, flags)
        return [ReString(item) for item in results if isinstance(item, str)]

    def findall(self, pattern: str, string: str, flags=0) -> List[Union[Any]]:
        results = re.findall(pattern, string, flags)
        return [ReString(item) for item in results if isinstance(item, str)]

    def finditer(self, pattern: str, string: str, flags=0) -> Iterator[re.Match[str]]:
        return re.finditer(pattern, string, flags)
