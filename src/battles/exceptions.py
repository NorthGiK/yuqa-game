class InvalidDeckSizeError(Exception):
    @property
    def message(self) -> str:
        return "Размер колоды игрока и необходимой для боя РАЗНЫЕ!"