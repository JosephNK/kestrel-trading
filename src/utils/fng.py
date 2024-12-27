import requests


class Fng:
    """
    암호화폐 시장의 Fear & Greed Index(공포와 탐욕 지수)를 가져오는 클래스

    Fear & Greed Index는 0~100 사이의 값으로:
    - 0-25: Extreme Fear (극도의 공포)
    - 26-45: Fear (공포)
    - 46-55: Neutral (중립)
    - 56-75: Greed (탐욕)
    - 76-100: Extreme Greed (극도의 탐욕)
    을 나타냅니다.
    """

    @staticmethod
    def get_fear_and_greed_index():
        """
        Alternative.me API에서 최신 Fear & Greed Index를 조회하는 메서드

        Returns:
            dict: 성공시 아래 형식의 딕셔너리 반환
                {
                    'value': '현재 인덱스 값',
                    'value_classification': '현재 상태 분류',
                    'timestamp': '데이터 시간stamp',
                    'time_until_update': '다음 업데이트까지 남은 시간'
                }
            None: API 호출 실패시
        """
        # Fear & Greed Index API 엔드포인트
        url = "https://api.alternative.me/fng/"

        # GET 요청 보내기
        response = requests.get(url)

        # 응답 상태 코드가 200(성공)인 경우
        if response.status_code == 200:
            data = response.json()  # JSON 응답을 파이썬 딕셔너리로 변환
            return data["data"][0]  # 최신 데이터(첫 번째 항목) 반환
        else:
            return None
