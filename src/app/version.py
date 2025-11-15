import re

import requests

CURRENT_VERSION = "3.0"

REPO = "shsh-x/sh-x-cleaner"
REPO_API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
REPO_RELEASE_URL = f"https://github.com/{REPO}/releases/latest"


def __get_latest_release_tag() -> str:
    api_url = f"https://api.github.com/repos/{REPO}/releases/latest"
    response = requests.get(api_url)
    response.raise_for_status()

    return response.json()['tag_name']


def __parse_version(ver: str) -> tuple:
    ver = re.sub(r'^[vV\.]+', '', ver)
    return tuple(map(int, re.split(r'[^\d]+', ver)))


def __is_new_version(version: str) -> bool:
    cur_version = __parse_version(CURRENT_VERSION)
    git_version = __parse_version(version)
    return git_version > cur_version


def check_for_updates() -> tuple[bool, str]:
    try:
        latest_version = __get_latest_release_tag()
        return __is_new_version(latest_version), latest_version
    except Exception:
        return False, ""
