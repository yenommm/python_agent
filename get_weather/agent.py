from langchain.agents import create_agent

from chapter02chat.get_weather import get_weather
from chapter02chat.get_time import get_time_info
from chapter02chat.model import model


class SmartAssistant:
    """多功能智能助手"""
    def __init__(self):
        # 初始化模型
        self.model = model
        # 工具列表
        self.tools = [
            get_weather,
            get_time_info,
        ]
        # 系统提示词
        system_prompt = """你是一个多功能智能助手，可以帮助用户：
          🌤 查询天气：使用 get_weather 工具
          ⏰ 时间查询：使用 get_time_info 工具
                 重要提示：
                 1. 仔细阅读用户问题，确定需要使用哪个工具
                 2. 如果需要多个工具，按顺序调用
                 3. 总是用友好、专业的语气回答
                 4. 如果工具返回了数据，要用通俗易懂的语言解释给用户
                 5. 如果无法完成任务，诚实地告诉用户原因
                 请始终使用中文回答。"""
        # ✅ 创建 agent
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=system_prompt
        )
        # 对话历史
        self.messages = []

    def chat(self, user_input: str) -> str:
        """对话接口"""
        # 添加用户消息
        self.messages.append({"role": "user", "content": user_input})
        # 调用 agent
        result = self.agent.invoke({"messages": self.messages})
        # 更新消息历史
        self.messages = result["messages"]
        # 返回最后一条 AI 消息
        for msg in reversed(self.messages):
            if msg.type == "ai" and msg.content:
                return msg.content
        return "抱歉，我无法处理这个请求。"

    def reset(self):
        """重置对话历史"""
        self.messages = []