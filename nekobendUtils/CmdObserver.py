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
        self.command = command
        self._thread = None
        self._is_running = False
        self._output_queue: queue.Queue[CmdObserver._Readline] = queue.Queue()
        self._stop_event = threading.Event()

    def __str__(self) -> str:
        return self.command

    def __repr__(self) -> str:
        return self.command

    def _run(self):
        try:
            self._process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout_thread = threading.Thread(target=self._read_stdout)
            stderr_thread = threading.Thread(target=self._read_stderr)

            stdout_thread.start()
            stderr_thread.start()

            self._process.wait()

            self._is_running = False

            stdout_thread.join()
            stderr_thread.join()

        except Exception as e:
            print(f"Error running command: {e}")

    def _auto_encoder(self, line: bytes) -> str:
        encode_list = ["utf-8", "shift-jis", "euc-jp", "cp932"]
        for encode in encode_list:
            try:
                return line.decode(encode)
            except UnicodeDecodeError:
                continue

    def _read_stdout(self):
        while self.is_running() and self._process.stdout:
            readline = self._process.stdout.readline().strip()
            if readline:
                self._put_output(stdout=self._auto_encoder(readline))

    def _read_stderr(self):
        while self.is_running() and self._process.stderr:
            readline = self._process.stderr.readline().strip()
            if readline:
                print(f"Warning: {readline}")
                self._put_output(stderr=self._auto_encoder(readline))

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

    def get(
        self, timeout: int = 1
    ) -> namedtuple("Readline", ["time", "stdout", "stderr"]) | None:
        try:
            return self._output_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_running(self) -> bool:
        return self._is_running and not self._stop_event.is_set()

    def start(self):
        self._is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self):
        self._is_running = False
        self._stop_event.set()
        if self._process:
            self._process.terminate()  # サブプロセスを終了
        self._thread.join()
