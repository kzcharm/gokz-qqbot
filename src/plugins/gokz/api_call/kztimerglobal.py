from datetime import datetime

from src.plugins.gokz.utils.kreedz import format_kzmode
from src.plugins.gokz.utils.steam_user import conv_steamid
from ..api_call.helper import fetch_get

GLOBAL_API_URL = "https://kztimerglobal.com/api/v2.0/"


async def fetch_global_stats(steamid64, mode_str, has_tp=True) -> list:
    steamid64 = conv_steamid(steamid64, 64)
    params = {
        'steamid64': steamid64,
        'tickrate': 128,
        'stage': 0,
        'modes_list_string': mode_str,
        'limit': 10000,
        'has_teleports': str(has_tp).lower(),
    }
    data = await fetch_get(f"{GLOBAL_API_URL}records/top", params=params)
    return data


async def fetch_personal_recent(steamid64, mode='kzt'):
    steamid64 = conv_steamid(steamid64, 64)
    mode = format_kzmode(mode)

    data_with_tp = await fetch_global_stats(steamid64, mode, True)
    data_without_tp = await fetch_global_stats(steamid64, mode, False)
    data = data_with_tp + data_without_tp

    for item in data:
        item["created_on_datetime"] = datetime.fromisoformat(item["updated_on"])
    sorted_data = sorted(data, key=lambda x: x["created_on_datetime"], reverse=True)

    return sorted_data[0]


async def fetch_personal_best(steamid64, map_name, mode='kzt', has_tp=True):
    steamid64 = conv_steamid(steamid64, 64)
    mode = format_kzmode(mode)

    params = {
        'steamid64': str(steamid64),
        'map_name': map_name,
        'stage': 0,
        'modes_list_string': mode,
        'has_teleports': str(has_tp).lower()
    }

    url = "https://kztimerglobal.com/api/v2.0/records/top"
    data = await fetch_get(url, params=params)
    if data:
        return data[0]
    else:
        return None


async def fetch_world_record(map_name, mode='kzt', has_tp=True):
    mode = format_kzmode(mode)
    params = {
        'map_name': map_name,
        'has_teleports': str(has_tp).lower(),
        'stage': 0,
        'modes_list_string': mode,
        'place_top_at_least': 1
    }

    data = await fetch_get(f"{GLOBAL_API_URL}records/top/recent", params=params)
    return data[0]


async def fetch_personal_purity(steamid64, mode='kzt', exclusive=False) -> dict:
    server_id = [1683, 1633, 1393]

    steamid64 = conv_steamid(steamid64, 64)
    mode = format_kzmode(mode)

    data_with_tp = await fetch_global_stats(steamid64, mode, True)
    data_without_tp = await fetch_global_stats(steamid64, mode, False)
    data = data_with_tp + data_without_tp

    maps = [f"{record['map_name']} {'TP' if record['teleports'] else 'PRO'}" for record in data if record['server_id'] != 1683]

    if exclusive:
        count = sum(1 for item in data if item.get('server_id') in server_id)
    else:
        count = sum(1 for item in data if item.get('server_id') == server_id[0])

    return {
        'name': data[0]['player_name'],
        'steamid64': steamid64,
        'count': count,
        'total': len(data),
        'percentage': count / len(data),
        'maps': maps,
    }
