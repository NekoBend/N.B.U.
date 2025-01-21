import subprocess
import platform

class Clipboard:
    __module__ = "NekoBendUtils"

    @staticmethod
    def copy_to_clipboard(text: str):
        if platform.system() == "Windows":
            subprocess.Popen(
                ["clip"],
                stdin=subprocess.PIPE,
                text=True,
            ).communicate(input=text)
        else:
            raise NotImplementedError("This function is only implemented for Windows.")

    @staticmethod
    def paste_from_clipboard() -> str:
        if platform.system() == "Windows":
            return subprocess.Popen(
                ["powershell", "-Command", "Get-Clipboard"],
                stdout=subprocess.PIPE,
                text=True,
            ).communicate()[0]
        else:
            raise NotImplementedError("This function is only implemented for Windows.")

    @staticmethod
    def clear_clipboard():
        if platform.system() == "Windows":
            subprocess.Popen(
                ["powershell", "-Command", "Set-Clipboard", "-Value", ""],
                stdout=subprocess.PIPE,
                text=True,
            ).communicate()
        else:
            raise NotImplementedError("This function is only implemented for Windows.")