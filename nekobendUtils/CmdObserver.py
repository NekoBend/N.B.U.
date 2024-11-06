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
        self.command: str = command
        self._thread: Optional[threading.Thread] = None
        self._is_running: bool = False
        self._output_queue: queue.Queue[CmdObserver._Readline] = queue.Queue()
        self._stop_event: threading.Event = threading.Event()
        self._process: Optional[subprocess.Popen] = None

    def __str__(self) -> str:
        return self.command

    def __repr__(self) -> str:
        return self.command

    def _run(self) -> None:
        try:
            self._process = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
            )

            stdout_thread: threading.Thread = threading.Thread(target=self._read_stdout)
            stderr_thread: threading.Thread = threading.Thread(target=self._read_stderr)

            stdout_thread.start()
            stderr_thread.start()

            self._process.wait()

            self._is_running = False

            stdout_thread.join()
            stderr_thread.join()

        except Exception as e:
            print(f"Error running command: {e}")

    def _auto_encoder(self, line: bytes) -> str:
        encode_list: list[str] = ["utf-8", "shift-jis", "euc-jp", "cp932"]
        for encode in encode_list:
            try:
                return line.decode(encode)
            except UnicodeDecodeError:
                continue
        return line.decode("utf-8", errors="ignore")

    def _read_stdout(self) -> None:
        while self.is_running() and self._process and self._process.stdout:
            readline: bytes = self._process.stdout.readline().strip()
            if readline:
                self._put_output(stdout=self._auto_encoder(readline))

    def _read_stderr(self) -> None:
        while self.is_running() and self._process and self._process.stderr:
            readline: bytes = self._process.stderr.readline().strip()
            if readline:
                print(f"Warning: {readline}")
                self._put_output(stderr=self._auto_encoder(readline))

    def _put_output(
        self, stdout: Optional[str] = None, stderr: Optional[str] = None
    ) -> None:
        self._output_queue.put(
            self._Readline(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                stdout,
                stderr,
            )
        )

    def is_empty(self) -> bool:
        return self._output_queue.empty()

    def get(self, timeout: int = 1) -> Optional[_Readline]:
        try:
            return self._output_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_running(self) -> bool:
        return self._is_running and not self._stop_event.is_set()

    def start(self) -> None:
        self._is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self) -> None:
        self._is_running = False
        self._stop_event.set()
        if self._process:
            self._process.terminate()
        if self._thread is not None:
            self._thread.join()
