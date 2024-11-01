import re
from typing import Union, List, Any, Iterator

class ReString(str):
    __module__ = "nekobendUtils"

    def __new__(cls, value: str) -> "ReString":
        return super().__new__(cls, value)  # type: ignore

    def to_string(self) -> str:
        return str(self)

    def match(self, pattern: str, flags=0) -> Union[re.Match[str], None]:
        return re.match(pattern, self, flags)

    def fullmatch(self, pattern: str, flags=0) -> Union[re.Match[str], None]:
        return re.fullmatch(pattern, self, flags)

    def search(self, pattern: str, flags=0) -> Union[re.Match[str], None]:
        return re.search(pattern, self, flags)

    def sub(self, pattern: str, repl: str, count: int = 0, flags=0) -> "ReString":
        result = re.sub(pattern, repl, self, count, flags)
        return ReString(result)

    def subn(
            self, pattern: str, repl: str, count: int = 0, flags=0
    ) -> tuple["ReString", int]:
        result, num_subs = re.subn(pattern, repl, self, count, flags)
        return ReString(result), num_subs

    def resplit(
            self, pattern: str, maxsplit: int = 0, flags=0
    ) -> List[Union["ReString", Any]]:
        results = re.split(pattern, self, maxsplit, flags)
        return [ReString(item) for item in results if isinstance(item, str)]

    def findall(self, pattern: str, flags=0) -> List[Union[Any]]:
        results = re.findall(pattern, self, flags)
        return [ReString(item) for item in results if isinstance(item, str)]

    def finditer(self, pattern: str, flags=0) -> Iterator[re.Match[str]]:
        return re.finditer(pattern, self, flags)

    # Overriding str methods to return ReString
    def __add__(self, other: str) -> "ReString":
        return ReString(super().__add__(other))

    def __getitem__(self, key: Union[int, slice]) -> "ReString":
        return ReString(super().__getitem__(key))

    def lower(self) -> "ReString":
        return ReString(super().lower())

    def upper(self) -> "ReString":
        return ReString(super().upper())

    def capitalize(self) -> "ReString":
        return ReString(super().capitalize())

    def title(self) -> "ReString":
        return ReString(super().title())

    def strip(self, chars: str = None) -> "ReString":
        return ReString(super().strip(chars))

    def lstrip(self, chars: str = None) -> "ReString":
        return ReString(super().lstrip(chars))

    def rstrip(self, chars: str = None) -> "ReString":
        return ReString(super().rstrip(chars))

    def replace(self, old: str, new: str, count: int = -1) -> "ReString":
        return ReString(super().replace(old, new, count))

    def split(self, sep: str = None, maxsplit: int = -1) -> List["ReString"]:
        return [ReString(item) for item in super().split(sep, maxsplit)]

    def join(self, iterable: List[str]) -> "ReString":
        return ReString(super().join(iterable))