import os
import sys
import json
import subprocess


class PwshRequests:
    pass


class CmdObserver:
    pass


class Clipboard:

    @staticmethod
    def copy(value: str):
        subprocess.Popen('clip', stdin=subprocess.PIPE, text=True).communicate(input=value)

    @staticmethod
    def paste() -> str:
        return subprocess.Popen('powershell -Command Get-Clipboard', stdout=subprocess.PIPE, text=True).communicate()[0]


class ReString(str):
    pass
