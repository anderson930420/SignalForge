import requests
import os
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv("API_KEY")
BASE_URL = "http://127.0.0.1:27123"

PROJECT_ROOT = "01 Projects"
PROJECT_NAME = "SignalForge"


def require_api_key():
    if not API_KEY:
        raise RuntimeError("Missing API_KEY. Please check your .env file.")


def vault_url(path):
    encoded_path = quote(path, safe="/")
    return f"{BASE_URL}/vault/{encoded_path}"


def read_file(path):
    require_api_key()

    url = vault_url(path)
    headers = {"Authorization": f"Bearer {API_KEY}"}

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return r.text

    if r.status_code == 404:
        return ""

    raise RuntimeError(
        f"Failed to read file: {path}\n"
        f"Status: {r.status_code}\n"
        f"Response: {r.text}"
    )


def main():
    project_path = f"{PROJECT_ROOT}/{PROJECT_NAME}/worklog.md"
    project = read_file(project_path)

    print("===== SIGNALFORGE WORKLOG =====")
    print(project)


if __name__ == "__main__":
    main()
