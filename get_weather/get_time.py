from datetime import datetime, timedelta
from langchain_core.tools import tool

@tool
def get_time_info(query_type: str = "current") -> str:
    """获取时间相关信息
    Args:
        query_type: 查询类型
            - "current": 当前时间
            - "date": 今天日期
            - "tomorrow": 明天日期
            - "yesterday": 昨天日期
            - "weekday": 星期几
    Returns:
        时间信息字符串
    Examples:
        get_time_info("current") 返回 "2025年1月25日 14:30:25"
        get_time_info("weekday") 返回 "星期六"
    """
    now = datetime.now()
    if query_type == "current":
        return now.strftime("当前时间：%Y年%m月%d日 %H:%M:%S")
    elif query_type == "date":
        return now.strftime("今天是：%Y年%m月%d日")
    elif query_type == "tomorrow":
        tomorrow = now + timedelta(days=1)
        return tomorrow.strftime("明天是：%Y年%m月%d日")
    elif query_type == "yesterday":
        yesterday = now - timedelta(days=1)
        return yesterday.strftime("昨天是：%Y年%m月%d日")
    elif query_type == "weekday":
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六",
"星期日"]
        return f"今天是{weekdays[now.weekday()]}"
    else:
        return f"不支持的查询类型：{query_type}。支持：current, date, tomorrow, yesterday, weekday"