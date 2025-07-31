from detoxify import Detoxify

detox = Detoxify('original')


def is_flagged(text: str) -> bool:
    try:
        scores = detox.predict(text)
        return scores['toxicity'] > 0.7
    except Exception as e:
        print(f"Detoxify error: {e}")
        return False
