import json
from pathlib import Path
from typing import Optional, Union

VALID_JSON_VALUES = Union[
    int,
    float,
    str,
    bool,
    None,
    dict[str, Union[int, float, str, bool, None, dict, list]],
    list[Union[int, float, str, bool, None, dict, list]],
]


class JsonDatabase:
    def __init__(self, location: Path) -> None:
        self.location = location
        self.database: dict[str, VALID_JSON_VALUES] = {}

    @property
    def database_dump(self) -> str:
        return json.dumps(self.database)

    @classmethod
    def from_location(cls, location: Union[str, Path]) -> "JsonDatabase":
        if isinstance(location, str):
            location = Path(location)

        db = cls(location.absolute())

        db.load()

        return db

    def load(self) -> None:
        if self.location.exists():
            self.database = json.loads(self.location.read_text())
        else:
            self.location.write_text(self.database_dump)

        return None

    def write_to_file(self) -> None:
        with self.location.open("w+") as f:
            f.seek(0)
            f.truncate()

            f.write(self.database_dump)

        return None

    def set(self, key: str, value: VALID_JSON_VALUES) -> None:
        self.database[key] = value
        self.write_to_file()

        return None

    def get(self, key: str) -> Optional[VALID_JSON_VALUES]:
        if key not in self.database:
            return None

        return self.database[key]

    def delete(self, key: str) -> None:
        if key not in self.database:
            return None

        del self.database[key]

        self.write_to_file()

        return None

    def reset_database(self) -> None:
        self.database = {}

        self.write_to_file()

        return None
