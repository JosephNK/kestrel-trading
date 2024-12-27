import os
import requests


class News:
    @staticmethod
    def get_google_news(query: str):
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        url = "https://serpapi.com/search.json"
        params = {"engine": "google_news", "q": query, "api_key": serpapi_key}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            data = response.json()

            news_results = data.get("news_results", [])
            headlines = []
            for item in news_results:
                headlines.append(
                    {"title": item.get("title", ""), "date": item.get("date", "")}
                )

            return headlines[:5]  # 최신 5개의 뉴스 헤드라인만 반환
        except requests.RequestException as e:
            print(f"Error fetching news: {e}")
            return []
