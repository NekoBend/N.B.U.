import queue
import subprocess
import threading
from collections import namedtuple
from datetime import datetime
from typing import Optional


class CmdObserver:
    __module__ = "nekobendUtils"
    _Readline = namedtuple("Readline", ["time", "stdout", "stderr"])

    def __init__(self, command: str) -> None:
        self._thread = None
        self.command = command
        self._is_running = False
        self._output_queue = queue.Queue()
        self._stop_event = threading.Event()

    def __str__(self) -> str:
        return self.command

    def __repr__(self) -> str:
        return self.command

    def _run(self):
        self._process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=65536,
            encoding="utf-8",
        )

        stdout_thread = threading.Thread(target=self._read_stdout)
        stderr_thread = threading.Thread(target=self._read_stderr)

        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()

        self._process.wait()

    def _read_stdout(self):
        readline: str | None = None

        while self.is_running():
            if self._process.stdout:
                readline = self._process.stdout.readline().strip()

            if readline:
                self._put_output(stdout=readline)

    def _read_stderr(self):
        readline: str | None = None

        while self.is_running():
            if self._process.stderr:
                readline = self._process.stderr.readline().strip()

            if readline:
                print(f"Warning: {readline}")
                self._put_output(stderr=readline)

    def _put_output(self, stdout: Optional[str] = None, stderr: Optional[str] = None):
        self._output_queue.put(
            self._Readline(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                stdout,
                stderr,
            )
        )

    def is_empty(self) -> bool:
        return self._output_queue.empty()

    def get(self, timeout: int = 1) -> dict | None:
        try:
            return self._output_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_running(self) -> bool:
        return self._is_running

    def start(self):
        self._is_running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self):
        self._is_running = False
        self._thread.join()
