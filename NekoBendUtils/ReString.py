import re
from typing import Union, List, Any, Iterator, SupportsIndex, Tuple, Optional, Iterable
from collections.abc import Iterable as _Iterable


class ReString(str):
    __module__ = "NekoBendUtils"

    def __new__(cls, value: str) -> "ReString":
        return super().__new__(cls, value)

    def to_string(self) -> str:
        return str(self)

    def print(self) -> None:
        print(self)

    def match(self, pattern: str, flags: int = 0) -> Optional[re.Match[str]]:
        return re.match(pattern, self, flags)

    def fullmatch(self, pattern: str, flags: int = 0) -> Optional[re.Match[str]]:
        return re.fullmatch(pattern, self, flags)

    def search(self, pattern: str, flags: int = 0) -> Optional[re.Match[str]]:
        return re.search(pattern, self, flags)

    def sub(
        self, pattern: str, repl: str, count: int = 0, flags: int = 0
    ) -> "ReString":
        return ReString(re.sub(pattern, repl, self, count, flags))

    def subn(
        self, pattern: str, repl: str, count: int = 0, flags: int = 0
    ) -> Tuple["ReString", int]:
        result, num_subs = re.subn(pattern, repl, self, count, flags)
        return ReString(result), num_subs

    def resplit(
        self, pattern: str, maxsplit: int = 0, flags: int = 0
    ) -> List["ReString"]:
        results = re.split(pattern, self, maxsplit, flags)
        return [ReString(item) for item in results if isinstance(item, str)]

    def findall(self, pattern: str, flags: int = 0) -> List[Any]:
        results = re.findall(pattern, self, flags)
        converted = []
        for item in results:
            if isinstance(item, str):
                converted.append(ReString(item))
            elif isinstance(item, tuple):
                converted.append(
                    tuple(ReString(x) if isinstance(x, str) else x for x in item)
                )
            else:
                converted.append(item)
        return converted

    def finditer(self, pattern: str, flags: int = 0) -> Iterator[re.Match[str]]:
        return re.finditer(pattern, self, flags)

    def __add__(self, other: str) -> "ReString":
        return ReString(super().__add__(other))

    def __getitem__(self, key: Union[SupportsIndex, slice]) -> "ReString":
        return ReString(super().__getitem__(key))

    def lower(self) -> "ReString":
        return ReString(super().lower())

    def upper(self) -> "ReString":
        return ReString(super().upper())

    def capitalize(self) -> "ReString":
        return ReString(super().capitalize())

    def title(self) -> "ReString":
        return ReString(super().title())

    def strip(self, chars: Optional[str] = None) -> "ReString":
        return ReString(super().strip(chars))

    def lstrip(self, chars: Optional[str] = None) -> "ReString":
        return ReString(super().lstrip(chars))

    def rstrip(self, chars: Optional[str] = None) -> "ReString":
        return ReString(super().rstrip(chars))

    def replace(self, old: str, new: str, count: SupportsIndex = -1) -> "ReString":
        return ReString(super().replace(old, new, count))

    def split(
        self, sep: Optional[str] = None, maxsplit: SupportsIndex = -1
    ) -> List["ReString"]:
        return [ReString(item) for item in super().split(sep, maxsplit)]

    def join(self, iterable: Iterable[Union[str, "ReString"]]) -> "ReString":
        return ReString(super().join(str(item) for item in iterable))

    def swapcase(self) -> "ReString":
        return ReString(super().swapcase())

    def zfill(self, width: int) -> "ReString":
        return ReString(super().zfill(width))

    def casefold(self) -> "ReString":
        return ReString(super().casefold())

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return super().encode(encoding, errors)
