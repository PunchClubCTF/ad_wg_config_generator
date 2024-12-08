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

    @config.setter
    def config(self, value):
        """
        Setter for configuration with basic validation
        """
        if value is not None:
            self._config = value
        else:
            raise ValueError("Configuration cannot be None")

