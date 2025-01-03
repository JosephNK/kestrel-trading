from pydantic import BaseModel, Field, field_validator


class SignupEmailParams(BaseModel):
    email: str = Field(
        ...,  # Required
        description="이메일",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        min_length=1,
    )
    password: str = Field(
        ...,  # Required
        description="비밀번호",
        pattern=r"^.*[A-Z].*\d.*$|^.*\d.*[A-Z].*$",
        min_length=8,
    )
