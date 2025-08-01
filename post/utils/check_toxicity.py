from detoxify import Detoxify

_detox_model = None


def get_detox_model():
    """
    caches the detox model
    :return:
    """
    global _detox_model
    if _detox_model is None:
        _detox_model = Detoxify('original')
    return _detox_model


def is_flagged(text: str) -> bool:
    """
    This method checks if a text is flagged.
    it uses detoxify to determine if the text is flagged.
    it returns True if the text is flagged.
    it returns False if the text is not flagged.
    :param text:
    :return:
    """
    try:
        model = get_detox_model()
        scores = model.predict(text)
        return scores['toxicity'] > 0.7
    except Exception as e:
        print(f"Detoxify error: {e}")
        return False
