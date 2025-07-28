import re


def extract_hashtags(text: str) -> list[str]:
    """
    Extracts hashtags from the given text (without the # symbol).
    """
    return [tag.strip("#") for tag in re.findall(r'#\w+', text)]
