class EdgeKey:
    def __init__(self, source_id: int, dest_id: int) -> None:
        self._source_id: int = source_id
        self._dest_id: int = dest_id

    @property
    def source_id(self) -> int:
        return self._source_id

    @property
    def dest_id(self) -> int:
        return self._dest_id

    def equals(self, other: "EdgeKey") -> bool:
        return self._source_id == other._source_id and self._dest_id == other._dest_id

    def hash_code(self) -> int:
        return hash((self._source_id, self._dest_id))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EdgeKey):
            return False
        return self.equals(other)

    def __hash__(self) -> int:
        return self.hash_code()

    def __repr__(self) -> str:
        return f"EdgeKey({self._source_id} -> {self._dest_id})"
