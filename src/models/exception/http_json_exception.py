class HttpJsonException(Exception):
    def __init__(self, status_code: int, error_message: str):
        super().__init__(error_message)
        self.status_code = status_code
        self.error_message = error_message
