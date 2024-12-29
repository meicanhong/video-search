import re
from typing import Optional


def format_duration(duration: str) -> Optional[str]:
    """将ISO 8601格式的时长转换为人类可读格式

    Args:
        duration: ISO 8601格式的时长字符串，如 'PT1H2M10S'

    Returns:
        str: 格式化后的时长字符串，如 '1小时2分钟10秒'

    Examples:
        >>> format_duration('PT1H2M10S')
        '1小时2分钟10秒'
        >>> format_duration('PT5M')
        '5分钟'
        >>> format_duration('PT30S')
        '30秒'
    """
    if not duration:
        return None

    # 使用正则表达式提取时、分、秒
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    if not match:
        return None

    hours, minutes, seconds = match.groups()

    # 构建人类可读的时长字符串
    parts = []
    if hours:
        parts.append(f"{int(hours)}小时")
    if minutes:
        parts.append(f"{int(minutes)}分钟")
    if seconds:
        parts.append(f"{int(seconds)}秒")

    return "".join(parts) if parts else None
