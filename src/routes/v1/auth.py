from typing import Any
from fastapi import Body, Request, status, APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from src.models.exception.http_json_exception import HttpJsonException
from src.models.params.signup_param import SignupEmailParams
from src.models.response.base_response_dto import BaseResponse
from src.models.user_dto import UserDto
from src.routes.dependencies.services import (
    get_supabase_service,
)

from src.services.supabase_service import SupabaseService
from src.utils.logging import Logging

# Router 생성
router = APIRouter()

security = HTTPBearer()


# # JWT 검증을 위한 의존성 함수
# async def verify_token(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     supabase: Client = Depends(get_supabase),
# ) -> dict:
#     try:
#         token = credentials.credentials
#         user = supabase.auth.get_user(token)
#         return user.model_dump()
#     except Exception as e:
#         raise JSONResponse(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             content={
#                 "statusCode": status.HTTP_401_UNAUTHORIZED,
#                 "errorMessage": "Invalid authentication credentials",
#             },
#         )


# Get Sign up password API (/api/v1/auth/signup/password)
@router.post(
    "/auth/signup/password",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[UserDto],
)
async def signup_email(
    params: SignupEmailParams = Body(...),
    supabase_service: SupabaseService = Depends(get_supabase_service),
):
    try:
        return supabase_service.sign_up_with_password(
            email=params.email,
            password=params.password,
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )


# Get Sign up password API (/api/v1/auth/signin/password)
@router.post(
    "/auth/signin/password",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[UserDto],
)
async def signup_email(
    params: SignupEmailParams = Body(...),
    supabase_service: SupabaseService = Depends(get_supabase_service),
):
    try:
        return supabase_service.sign_in_with_password(
            email=params.email,
            password=params.password,
        )
    except HttpJsonException as e:
        raise e
    except Exception as e:
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
