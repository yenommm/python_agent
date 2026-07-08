from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv(override=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY")
QWEATHER_BASE_URL = os.getenv("QWEATHER_BASE_URL")
EXIT_WORD = "quit"
model = init_chat_model(
    model="deepseek-chat",           # ← 换成标准模型，支持 tool calling
    model_provider="deepseek",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)