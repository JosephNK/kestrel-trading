import os

from colorama import Fore
from colorama import init as colorama_init


class Logging:

    @staticmethod
    def init():
        colorama_init()

    @staticmethod
    def langSmith(project_name=None, set_enable=True):
        if set_enable:
            result = os.environ.get("LANGCHAIN_API_KEY")
            if result is None or result.strip() == "":
                Logging.info("LangChain API Key가 설정되지 않았습니다.")
                return
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = project_name
            Logging.info(f"LangSmith Enabled. (Project Name : {project_name})")
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            Logging.info("LangSmith Disabled.")

    @staticmethod
    def error(msg, error):
        print(f"{Fore.RED}[ERROR]{Fore.RESET} {msg}", error)

    @staticmethod
    def info(msg):
        print(f"{Fore.GREEN}[INFO]{Fore.RESET} {msg}")

    @staticmethod
    def warning(msg):
        print(f"{Fore.YELLOW}[WARNING]{Fore.RESET} {msg}")
