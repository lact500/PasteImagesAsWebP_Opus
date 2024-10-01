import subprocess
from typing import Optional

from aqt.qt import *
from aqt.utils import showWarning

from ..ajt_common.utils import find_executable as find_executable_ajt
from ..config import config
from ..consts import ADDON_FULL_NAME, SUPPORT_DIR

AUDIO_FORMATS = config.COMMON_AUDIO_FORMATS

class FFmpegNotFoundError(FileNotFoundError):
    pass

def find_ffmpeg_exe() -> Optional[str]:
    return find_executable_ajt("ffmpeg")

class AudioConverter:

    def convert_audio(self, source_path: str, destination_path: str) -> None:
        if not find_ffmpeg_exe():
            raise FFmpegNotFoundError("ffmpeg executable is not in PATH")

        args = [
            find_ffmpeg_exe(),
            "-i", source_path,
            "-c:a", "libopus",
            "-c:v", "copy",
            "-vbr", "on",
            "-compression_level", "10",
            "-map", "0:a",
            "-application", "audio",
            *config["ffmpeg_audio_args"],
            destination_path
        ]

        print(f"executing args: {args}")
        p = subprocess.Popen(
            args,
            shell=False,
            bufsize=-1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding="utf8",
        )

        stdout, stderr = p.communicate()

        if p.wait() != 0:
            print("Conversion failed.")
            print(f"exit code = {p.returncode}")
            print(stdout)
            raise RuntimeError(f"Conversion failed with code {p.returncode}.")
