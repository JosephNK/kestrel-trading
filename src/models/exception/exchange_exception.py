class ExchangeException(Exception):
    def __init__(self, error_message: str):
        super().__init__(error_message)
        self.msg = error_message
