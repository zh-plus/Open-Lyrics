import json
import sys
from dataclasses import dataclass
from typing import List, Union

from openlrc.logger import logger
from openlrc.utils import format_timestamp, change_ext


@dataclass
class Element:
    """
    Save a LRC format element.
    """
    start: float
    end: Union[float, None]
    text: str

    @property
    def duration(self):
        if self.end:
            return self.end - self.start
        else:
            return sys.maxsize  # Fake int infinity

    def to_json(self):
        return {'start': self.start, 'end': self.end, 'text': self.text}


class Subtitle:
    """
    Save a sequence of Element, and meta data.
    """

    def __init__(self, filename):
        self.filename = filename
        with open(filename, encoding='utf-8') as f:
            content = json.loads(f.read())

        self.lang = content['language']
        self.generator = content['generator']
        self.segments: List[Element] = [Element(**seg) for seg in content['segments']]

    def get_texts(self):
        return [e.text for e in self.segments]

    def set_texts(self, texts):
        # Check length
        assert len(texts) == len(self.segments)

        for i, text in enumerate(texts):
            self.segments[i].text = text

    def save(self, filename, update_name=False):
        results = {
            'language': self.lang,
            'generator': self.generator,
            'segments': [seg.to_json() for seg in self.segments]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        if update_name:
            self.filename = filename

        return filename

    def to_lrc(self):
        """
        Save lrc file.
        """
        lrc_name = change_ext(self.filename, 'lrc')
        with open(lrc_name, 'w', encoding='utf-8') as f:
            print(f'LRC generated by https://github.com/zh-plus/Open-Lyrics, lang={self.lang}', file=f, flush=True)
            for i, segment in enumerate(self.segments):
                print(
                    f'[{format_timestamp(segment.start)}] {segment.text}',
                    file=f,
                    flush=True,
                )
                if i == len(self.segments) - 1 or segment.end != self.segments[i + 1].start:
                    print(f'[{format_timestamp(segment.end)}]', file=f, flush=True)

        logger.info(f'File saved to {lrc_name}')