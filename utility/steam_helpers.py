import xml.etree.ElementTree as ET

import httpx


def get_steam_username(steam_id: int) -> str:
    """
    Helper function to return a steam username from a steam id
    :param steam_id: int of steam user id
    :return:
    """
    url = f"https://steamcommunity.com/profiles/{steam_id}/?xml=1"
    r = httpx.get(url)

    tree = ET.fromstring(r.content)

    return tree.find("steamID").text
