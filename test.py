from steam.steamid import SteamID


def conv_steamid(steamid, target_type: int | str = 2, url=False):
    steamid = SteamID(steamid)
    if steamid.is_valid() is False:
        raise ValueError(f"Invalid SteamID: {steamid}")

    if url:
        return steamid.community_url

    if target_type == '64':
        return str(steamid.as_64)

    target_type = int(target_type)

    if target_type == 2:
        return steamid.as_steam2
    if target_type == 3:
        return steamid.as_steam3
    if target_type == 32:
        return steamid.as_32
    if target_type == 64:
        return steamid.as_64
    if target_type == 0:
        return {
            "steam2": steamid.as_steam2,
            "steam3": steamid.as_steam3,
            "steam64": steamid.as_64,
            "steam32": steamid.as_32,
            "url": steamid.community_url,
        }

    raise ValueError(f"Invalid target type: {target_type}")


conv_steamid('Exa')
