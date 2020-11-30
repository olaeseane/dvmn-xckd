from pathlib import Path
import requests


def download_image(url, name):
    Path.cwd().mkdir(parents=False, exist_ok=True)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    with open(f"{Path.cwd()}/{name}", "wb") as file:
        file.write(response.content)