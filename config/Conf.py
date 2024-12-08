class Conf:
    def __init__(self):
        self._config = ""

    def append_config(self, text: str) -> None:
        """Append text to the configuration"""
        self._config += text

    @property
    def config(self) -> str:
        """Get the complete configuration"""
        return self._config
