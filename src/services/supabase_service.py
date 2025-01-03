from os import getenv
from typing import Any
from fastapi import Body, status, APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client, create_client

from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.base_response_dto import BaseResponse
from src.models.session_dto import SessionDto
from src.models.user_dto import UserDto


class SupabaseService:
    supabase: Client

    def __init__(self):
        supabase_url = getenv("SUPABASE_URL")
        supabase_key = getenv("SUPABASE_API_KEY")
        self.supabase = create_client(supabase_url, supabase_key)

    def sign_up_with_password(
        self,
        email: str,
        password: str,
    ) -> BaseResponse[UserDto]:
        try:
            response = self.supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "redirect_to": "http://127.0.0.1:8010/api/v1/auth/verify/confirm-signup",
                    },
                }
            )

            # data = response.model_dump()
            # print("data", data)
            user = response.user
            print("user", user)
            session = response.session
            access_token = session.access_token if session is not None else None
            refresh_token = session.refresh_token if session is not None else None

            user_dto = UserDto(
                id=user.id,
                provider=(
                    user.app_metadata.get("provider")
                    if user and hasattr(user, "app_metadata") and user.user_metadata
                    else None
                ),
                email=(
                    user.user_metadata.get("email")
                    if user and hasattr(user, "user_metadata") and user.user_metadata
                    else None
                ),
                email_verified=(
                    user.user_metadata.get("email_verified")
                    if user and hasattr(user, "user_metadata") and user.user_metadata
                    else False
                ),
                session=(
                    SessionDto(
                        access_token=access_token,
                        refresh_token=refresh_token,
                    )
                    if session is not None
                    else None
                ),
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

            return BaseResponse[UserDto](
                status_code=status.HTTP_200_OK,
                item=user_dto,
            )
        except HttpJsonException as e:
            raise e
        except Exception as e:
            raise HttpJsonException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
            )

    def sign_in_with_password(
        self,
        email: str,
        password: str,
    ) -> BaseResponse[UserDto]:
        try:
            response = self.supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )

            # data = response.model_dump()
            user = response.user
            session = response.session
            access_token = session.access_token if session is not None else None
            refresh_token = session.refresh_token if session is not None else None

            user_dto = UserDto(
                id=user.id,
                provider=user.app_metadata["provider"],
                email=user.user_metadata["email"],
                email_verified=user.user_metadata["email_verified"],
                session=(
                    SessionDto(
                        access_token=access_token,
                        refresh_token=refresh_token,
                    )
                    if session is not None
                    else None
                ),
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

            return BaseResponse[UserDto](
                status_code=status.HTTP_200_OK,
                item=user_dto,
            )
        except HttpJsonException as e:
            raise e
        except Exception as e:
            raise HttpJsonException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
            )
