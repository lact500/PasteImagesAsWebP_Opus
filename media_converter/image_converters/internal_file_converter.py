# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import os.path
from typing import Optional

import aqt.editor
from anki.notes import Note
from aqt import mw
from aqt.qt import *

from ..utils.file_paths_factory import FilePathFactory
from .common import ImageDimensions
from .image_converter import ImageConverter
from .audio_converter import AudioConverter, AUDIO_FORMATS

class InternalFileConverter:
    """
    Converter used when converting an image or audio file already stored in the collection (e.g. bulk-convert).
    """

    _note: Note
    _initial_file_path: str
    _initial_dimensions: Optional[ImageDimensions]
    _destination_file_path: str
    _conversion_finished: bool

    def __init__(self, editor: Optional[aqt.editor.Editor], note: Note, initial_filename: str):
        self._conversion_finished = False
        self._note = note
        self._fpf = FilePathFactory(note=note, editor=editor)
        self._initial_file_path = os.path.join(self._dest_dir, initial_filename)
        self._initial_dimensions = self.load_internal(initial_filename) if not self.is_audio_file(initial_filename) else None
        self._destination_file_path = self._fpf.make_unique_filepath(self._dest_dir, initial_filename)
        self._converter = ImageConverter(self._initial_dimensions) if not self.is_audio_file(initial_filename) else AudioConverter()

    @property
    def _dest_dir(self) -> str:
        assert mw
        return mw.col.media.dir()

    @property
    def new_file_path(self) -> str:
        if not self._conversion_finished:
            raise RuntimeError("Conversion wasn't performed.")
        return self._destination_file_path

    @property
    def new_filename(self) -> str:
        return os.path.basename(self.new_file_path)

    @property
    def initial_dimensions(self) -> Optional[ImageDimensions]:
        return self._initial_dimensions

    def is_audio_file(self, filename: str) -> bool:
        return os.path.splitext(filename)[1].lower() in AUDIO_FORMATS

    def load_internal(self, initial_filename: str) -> ImageDimensions:
        with open(os.path.join(self._dest_dir, initial_filename), "rb") as f:
            image = QImage.fromData(f.read())  # type: ignore
        return ImageDimensions(image.width(), image.height())

    def convert_internal(self) -> None:
        self._converter.convert_image(
            source_path=self._initial_file_path,
            destination_path=self._destination_file_path,
        )
        self._conversion_finished = True

    def convert_internal_audio(self) -> None:
        self._converter.convert_audio(
            source_path=self._initial_file_path,
            destination_path=self._destination_file_path,
        )
        self._conversion_finished = True
