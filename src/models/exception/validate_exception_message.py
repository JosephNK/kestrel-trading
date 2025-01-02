class ValidateExceptionMessage:
    field: str
    message: str

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

    def __str__(self) -> str:
        return f"Field: '{self.field}', Validation Failed: {self.message}"
