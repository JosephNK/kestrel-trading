import os
import requests
import time
from datetime import datetime


class EtherscanWhaleTransaction:
    api_key: str

    def __init__(self):
        self.api_key = os.environ.get("ETHERSCAN_API_KEY")

    def get_whale_transactions(self, min_value=1):
        """
        BSCScan API를 사용하여 BTC(BNB BEP20) 토큰의 대규모 거래를 모니터링하는 함수
        min_value: BTC 단위로의 최소 거래액 (예: 1 BTC)
        """

        # BTC 토큰 컨트랙트 주소 (BEP20)
        WBTC_CONTRACT = (
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"  # BTCB 컨트랙트 주소
        )

        # Etherscan API 엔드포인트
        url = "https://api.etherscan.io/api"

        # API 파라미터
        params = {
            "module": "account",
            # "action": "txlist",
            # "address": "your_address",  # 모니터링하고 싶은 특정 주소
            "action": "tokentx",  # 토큰 거래 조회
            "contractaddress": WBTC_CONTRACT,
            "startblock": "0",
            "endblock": "999999999",
            "page": "1",
            "offset": "100",  # 한 번에 가져올 거래 수
            "sort": "desc",
            "apikey": self.api_key,
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] == "1":  # API 호출 성공
                transactions = data["result"]
                whale_txs = []

                for tx in transactions:
                    # Wei를 BNB로 변환 (1 BNB = 10^18 Wei)
                    value_bnb = float(tx["value"]) / 10**18

                    if value_bnb >= min_value:
                        whale_txs.append(
                            {
                                "hash": tx["hash"],
                                "from": tx["from"],
                                "to": tx["to"],
                                "value_bnb": value_bnb,
                                "timestamp": datetime.fromtimestamp(
                                    int(tx["timeStamp"])
                                ),
                            }
                        )

                return whale_txs

            else:
                print(f"API 오류: {data}")
                return None

        except Exception as e:
            print(f"오류 발생: {str(e)}")
            return None

    def monitor_btc_whales(self, interval=300):  # 5분마다 체크
        """
        지속적으로 BTC 고래 활동을 모니터링하는 함수
        """
        print("BTC(BEP20) 고래 거래 모니터링 시작...")

        while True:
            print("\n거래 확인 중...")
            transactions = self.get_whale_transactions()

            if transactions:
                for tx in transactions:
                    print(
                        f"""
                    거래 해시: {tx['hash']}
                    보내는 주소: {tx['from']}
                    받는 주소: {tx['to']}
                    금액: {tx['value_btc']:.8f} BTC
                    시간: {tx['timestamp']}
                    """
                    )

            time.sleep(interval)

    def get_historical_wbtc_transactions(
        self,
        start_date=None,
        end_date=None,
        start_block=None,
        end_block=None,
        min_value=1,
    ):
        """
        특정 기간 또는 블록 범위의 WBTC 거래 이력을 조회
        start_date: 시작 날짜 (예: '2024-01-01')
        end_date: 종료 날짜 (예: '2024-12-31')
        start_block: 시작 블록 번호
        end_block: 종료 블록 번호
        min_value: 최소 WBTC 거래량
        """

        WBTC_CONTRACT = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"

        url = "https://api.etherscan.io/api"

        # 날짜가 제공된 경우 블록 번호로 변환
        if start_date and end_date:
            # 날짜를 타임스탬프로 변환
            start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

            # 해당 타임스탬프의 블록 번호 조회
            block_params = {
                "module": "block",
                "action": "getblocknobytime",
                "timestamp": start_timestamp,
                "closest": "before",
                "apikey": self.api_key,
            }
            response = requests.get(url, params=block_params)
            start_block = int(response.json()["result"])

            block_params["timestamp"] = end_timestamp
            response = requests.get(url, params=block_params)
            end_block = int(response.json()["result"])

        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": WBTC_CONTRACT,
            "startblock": start_block if start_block else "0",
            "endblock": end_block if end_block else "999999999",
            "page": "1",
            "offset": "10000",  # 한 번에 가져올 최대 거래 수
            "sort": "desc",
            "apikey": self.api_key,
        }

        all_transactions = []
        page = 1

        params["page"] = str(page)
        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data["status"] == "1":
                transactions = data["result"]
                if not transactions:  # 더 이상 거래가 없으면 종료
                    return all_transactions

                for tx in transactions:
                    value_wbtc = float(tx["value"]) / 10**8
                    if value_wbtc >= min_value:
                        tx_info = {
                            "hash": tx["hash"],
                            "from": tx["from"],
                            "to": tx["to"],
                            "value_wbtc": value_wbtc,
                            "block_number": int(tx["blockNumber"]),
                            "gas_price": float(tx["gasPrice"]) / 10**18,
                            "timestamp": datetime.fromtimestamp(int(tx["timeStamp"])),
                        }
                        all_transactions.append(tx_info)

                print(f"페이지 {page} 처리 완료: {len(transactions)} 거래 검색됨")
            else:
                print(f"API 오류: {data}")
        except Exception as e:
            print(f"오류 발생: {str(e)}")

        return all_transactions

    def print_transaction_summary(self, transactions):
        """거래 데이터 요약 출력"""
        if not transactions:
            print("거래 내역이 없습니다.")
            return

        total_volume = sum(tx["value_wbtc"] for tx in transactions)
        avg_volume = total_volume / len(transactions)
        max_tx = max(transactions, key=lambda x: x["value_wbtc"])

        print(f"\n=== 거래 요약 ===")
        print(f"총 거래 수: {len(transactions)}")
        print(f"총 거래량: {total_volume:.2f} WBTC")
        print(f"평균 거래량: {avg_volume:.2f} WBTC")
        print(f"최대 거래량: {max_tx['value_wbtc']:.2f} WBTC (해시: {max_tx['hash']})")
        print(
            f"조회 기간: {min(tx['timestamp'] for tx in transactions)} ~ {max(tx['timestamp'] for tx in transactions)}"
        )
