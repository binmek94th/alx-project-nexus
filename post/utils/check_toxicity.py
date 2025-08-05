import requests

from alx_project_nexus.settings import MODEL_API_URL
from alx_project_nexus.settings import MODEL_API_TOKEN


TOXIC_LABELS = {"toxic", "insult", "obscene", "threat", "identity_hate"}
THRESHOLD = 0.5

def is_flagged(text: str) -> bool:
    try:
        response = make_request(text)
        predictions = response[0]

        for pred in predictions:
            label = pred["label"]
            score = pred["score"]
            if label in TOXIC_LABELS and score >= THRESHOLD:
                return True

        return False
    except Exception as e:
        print(f"Error in is_flagged: {e}")
        return False


def make_request(text: str):
    headers = {
        "Authorization": f"Bearer {MODEL_API_TOKEN}"
    }

    response = requests.post(MODEL_API_URL, headers=headers, json={"inputs": text})
    response.raise_for_status()
    return response.json()
