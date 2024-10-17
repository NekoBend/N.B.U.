# import asyncio
# import functools
# import io
import os
import json
# import multiprocessing
import queue
import re
# import select
import subprocess
import threading
# import time
import hashlib
from collections import namedtuple

from datetime import datetime
from typing import Union, List, Any, Iterator


class PwshRequests:

    @staticmethod
    def _calculate_hash(data_json):
        sha256 = hashlib.sha256()
        sha256.update(data_json.encode('utf-8'))
        return sha256.hexdigest()

    @staticmethod
    def _run_ps1_script(data_json, cache_dir):
        command = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'REQUESTS.PS1', '-dataJson', data_json, '-dir', cache_dir]
        result = subprocess.run(command, capture_output=True, text=True)
        return result

    @staticmethod
    def _load_from_cache(hash_name, cache_dir):
        cache_file = os.path.join(cache_dir, f"{hash_name}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    @staticmethod
    def request(method, url, headers=None, data=None, cache=False, cache_dir=".\\.cache"):
        if method.upper() in ['PUT', 'DELETE']:
            cache = False
        if cache and not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        request_dict = {"URL": url, "Method": method.upper(), "Headers": headers or {}, "Body": data or {}}
        data_json = json.dumps(request_dict)
        hash_name = PwshRequests._calculate_hash(data_json)

        if cache:
            cached_response = PwshRequests._load_from_cache(hash_name, cache_dir)
            if cached_response is not None:
                return cached_response

        result = PwshRequests._run_ps1_script(data_json, cache_dir)

        if result.returncode != 0:
            raise Exception(f"Request failed: {result.stderr}")

        response_content = result.stdout

        if cache:
            cache_file = os.path.join(cache_dir, f"{hash_name}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(response_content)

        return response_content

    @staticmethod
    def get(url, headers=None, cache=False, cache_dir=".\\.cache"):
        return PwshRequests.request('GET', url, headers=headers, cache=cache, cache_dir=cache_dir)

    @staticmethod
    def post(url, headers=None, data=None, cache=False, cache_dir=".\\.cache"):
        return PwshRequests.request('POST', url, headers=headers, data=data, cache=cache, cache_dir=cache_dir)

    @staticmethod
    def put(url, headers=None, data=None):
        return PwshRequests.request('PUT', url, headers=headers, data=data)

    @staticmethod
    def delete(url, headers=None):
        return PwshRequests.request('DELETE', url, headers=headers)


class CmdObserver:
    _is_running = False
    _readline = namedtuple('Readline', ['time', 'stdout', 'stderr'])
    _output = queue.Queue()

    def __init__(self, cmd: str) -> None:
        self.cmd = cmd

    def __str__(self) -> str:
        return self.cmd

    def __repr__(self) -> str:
        return self.cmd

    def _run(self):
        self._process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=65536, encoding='utf-8')

        stdout_thread = threading.Thread(target=self._read_stdout)
        stderr_thread = threading.Thread(target=self._read_stderr)

        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()

        self._process.terminate()

    def _read_stdout(self):
        while self._is_running:
            readline = self._process.stdout.readline().strip()

            if readline:
                self._put(stdout=readline)

    def _read_stderr(self):
        while self._is_running:
            readline = self._process.stderr.readline().strip()

            if readline:
                print(f'Warning: {readline}')
                self._put(stderr=readline)

    def _put(self, stdout: str = None, stderr: str = None):
        self._output.put(self._readline(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            stdout,
            stderr,
        ))

    def is_empty(self) -> bool:
        return self._output.empty()

    def get(self, timeout: int = 1) -> dict | None:
        try:
            return self._output.get(timeout=timeout)

        except queue.Empty:
            return False

    def is_running(self) -> bool:
        return self._is_running

    def start(self):
        self._is_running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self):
        self._is_running = False
        self._thread.join()


class Clipboard:

    @staticmethod
    def copy(value: str):
        subprocess.Popen('clip', stdin=subprocess.PIPE, text=True).communicate(input=value)

    @staticmethod
    def paste() -> str:
        return subprocess.Popen('powershell -Command Get-Clipboard', stdout=subprocess.PIPE, text=True).communicate()[0]


class ReString(str):

    def __new__(cls, value: str) -> 'ReString':
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return self

    def __repr__(self) -> str:
        return self

    def to_string(self) -> str:
        return str(self)

    def match(self, pattern: str, flags=0) -> Union[re.Match[str], None]:
        return re.match(pattern, self, flags)

    def fullmatch(self, pattern: str, flags=0) -> Union[re.Match[str], None]:
        return re.fullmatch(pattern, self, flags)

    def search(self, pattern: str, flags=0) -> Union[re.Match[str], None]:
        return re.search(pattern, self, flags)

    def sub(self, pattern: str, repl: str, count: int = 0, flags=0) -> 'ReString':
        result = re.sub(pattern, repl, self, count, flags)
        return ReString(result)

    def subn(self, pattern: str, repl: str, count: int = 0, flags=0) -> tuple['ReString', int]:
        result, num_subs = re.subn(pattern, repl, self, count, flags)
        return ReString(result), num_subs

    def resplit(self, pattern: str, maxsplit: int = 0, flags=0) -> List[Union['ReString', Any]]:
        results = re.split(pattern, self, maxsplit, flags)
        return [ReString(item) for item in results if isinstance(item, str)]

    def findall(self, pattern: str, flags=0) -> List[Union[Any]]:
        results = re.findall(pattern, self, flags)
        return [ReString(item) for item in results if isinstance(item, str)]

    def finditer(self, pattern: str, flags=0) -> Iterator[re.Match[str]]:
        return re.finditer(pattern, self, flags)
