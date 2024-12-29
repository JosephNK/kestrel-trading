from fastapi import status, APIRouter
from src.models.exception.http_json_exception import HttpJsonException
from src.models.response.health_response_dto import HealthResponseDto
from src.utils.logging import Logging

# Router 생성
router = APIRouter()


# Get Health API
@router.get("/", status_code=status.HTTP_200_OK, response_model=HealthResponseDto)
async def health():
    """
    서버 상태 확인

    Args:
        None
    Returns:
        HealthResponseDto
    """
    try:
        return HealthResponseDto(status="OK")
    except Exception as e:
        print("Exception occurred:", e)
        raise HttpJsonException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message=str(e)
        )
