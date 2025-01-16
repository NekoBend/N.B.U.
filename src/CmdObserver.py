import queue
import subprocess
import threading
import warnings

from collections import namedtuple
from datetime import datetime
from typing import Optional, List, Union


class CmdObserver:
    __module__ = "nekobendUtils"
    _Readline = namedtuple("Readline", ["time", "stdout", "stderr"])

    def __init__(self, command: str, is_realtime: bool = False) -> None:
        self.command: str = command
        self.is_realtime: bool = is_realtime
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
                self.command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )

            stdout_thread = threading.Thread(target=self._read_stdout)
            stderr_thread = threading.Thread(target=self._read_stderr)

            stdout_thread.start()
            stderr_thread.start()

            self._process.wait()

            self._is_running = False
            self._stop_event.set()

            stdout_thread.join()
            stderr_thread.join()

        except Exception as e:
            warnings.warn(f"Error running command: {e}")

    @staticmethod
    def _auto_encoder(line: bytes) -> str:
        encode_list: List[str] = ["utf-8", "shift-jis", "euc-jp", "cp932"]
        for encode in encode_list:
            try:
                return line.decode(encode)
            except UnicodeDecodeError:
                continue
        return line.decode("utf-8", errors="ignore")

    def _read_stdout(self) -> None:
        if self._process and self._process.stdout:
            for readline in iter(self._process.stdout.readline, b""):
                if readline:
                    decoded_line = self._auto_encoder(readline.strip())
                    self._put_output(stdout=decoded_line, stderr=None)
                    if self.is_realtime:
                        warnings.warn(decoded_line)

    def _read_stderr(self) -> None:
        if self._process and self._process.stderr:
            for readline in iter(self._process.stderr.readline, b""):
                if readline:
                    decoded_line = self._auto_encoder(readline.strip())
                    warnings.warn(f"Warning: {decoded_line}")
                    self._put_output(stderr=decoded_line)
                    if self.is_realtime:
                        warnings.warn(decoded_line)

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

    def get(self, timeout: int = 1) -> Union[List[Optional[_Readline]], Optional[_Readline]]:
        try:
            if not self.is_realtime:
                outputs = []

                while not self.is_empty():
                    if output := self._output_queue.get(timeout=timeout):
                        outputs.append(output)

                return outputs

            else:
                return self._output_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_running(self) -> bool:
        return self._is_running and not self._stop_event.is_set()

    def start(self) -> Union[subprocess.Popen, str, None]:
        if not self._is_running:
            self._is_running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

            if not self.is_realtime:
                self._thread.join()

    def stop(self) -> None:
        if self._is_running:
            self._is_running = False
            self._stop_event.set()
            if self._process:
                if self._process.poll() is None:
                    self._process.kill()

            if self._thread is not None:
                self._thread.join()
