import subprocess


class Clipboard:
    __module__ = "nekobendUtils"

    @staticmethod
    def copy_to_clipboard(text: str):
        subprocess.Popen(
            "clip",
            stdin=subprocess.PIPE,
            text=True,
        ).communicate(input=text)

    @staticmethod
    def paste_from_clipboard() -> str:
        return subprocess.Popen(
            "powershell -Command Get-Clipboard",
            stdout=subprocess.PIPE,
            text=True,
        ).communicate()[0]

    @staticmethod
    def clear_clipboard():
        subprocess.Popen(
            'powershell -Command Set-Clipboard -Value ""',
            stdout=subprocess.PIPE,
            text=True,
        ).communicate()
