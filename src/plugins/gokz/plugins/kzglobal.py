from datetime import datetime
from pathlib import Path
from textwrap import dedent
from zoneinfo import ZoneInfo

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.params import CommandArg

from ..api_call.kztimerglobal import fetch_personal_best, fetch_personal_recent, fetch_world_record, fetch_personal_bans
from ..bot_utils.command_helper import CommandData
from ..utils.config import MAP_TIERS
from ..utils.formatter import format_gruntime, record_format_time
from ..utils.kreedz import search_map
from ..utils.kz.screenshot import vnl_screenshot_async, kzgoeu_screenshot_async, random_card
from ..utils.map_img_url import get_map_img_url

pb = on_command('pb', aliases={'personal-best'})
pr = on_command('pr')
kz = on_command('kz', aliases={'kzgo'})
wr = on_command('wr')
ban_ = on_command('ban')

private_map_names: dict[int, str] = {}  # For private messages
group_map_names: dict[int, str] = {}  # For group messages

DEFAULT_MAP = 'bkz_cakewalk'


def convert_to_shanghai_time(date_str):
    """Converts a given datetime string to Asia/Shanghai timezone, handling future dates."""
    original_time = datetime.fromisoformat(date_str)

    # Check for far-future expiration date
    if original_time.year >= 9999:
        return "永久封禁"  # "Permanent Ban" in Chinese

    # Otherwise, convert to Shanghai time
    shanghai_time = original_time.astimezone(ZoneInfo("Asia/Shanghai"))
    return shanghai_time.strftime("%Y-%m-%d %H:%M:%S")


@ban_.handle()
async def _(event: Event, args: Message = CommandArg()):
    cd = CommandData(event, args)
    if cd.error:
        return await ban_.send(cd.error)

    bans = await fetch_personal_bans(steamid64=cd.steamid)

    if not bans:
        return await ban_.finish(f"{cd.steamid} 没有找到任何封禁记录。", at_sender=True)

    content = f"玩家: {cd.steamid} 的封禁记录\n"

    for ban in bans:
        ban_type = ban.get("ban_type", "未知")
        player_name = ban.get("player_name", "未知玩家")
        notes = ban.get("notes", "无")
        server_id = ban.get("server_id", "未知服务器")

        created_on = convert_to_shanghai_time(ban["created_on"])
        expires_on = convert_to_shanghai_time(ban["expires_on"])

        content += dedent(f"""
            ╔═════════════
            ║ 玩家: {player_name}
            ║ 封禁类型: {ban_type}
            ║ 服务器ID: {server_id}
            ║ 创建时间: {created_on}
            ║ 解封时间: {expires_on}
            ║ 备注: {notes}
            ╚═════════════
        """).strip() + '\n'

    await ban_.send(content, at_sender=True)


@wr.handle()
async def _(event: Event, args: Message = CommandArg()):
    cd = CommandData(event, args)
    if cd.error:
        return await wr.finish(cd.error)

    if not cd.args:
        if isinstance(event, GroupMessageEvent):
            map_name = group_map_names.get(event.group_id, DEFAULT_MAP)
        elif isinstance(event, PrivateMessageEvent):
            map_name = private_map_names.get(event.user_id, DEFAULT_MAP)
        else:
            map_name = DEFAULT_MAP

        if not map_name:
            return await wr.finish("🗺地图名都不给我怎么帮你查WR (￣^￣) ")
    else:
        map_name = search_map(cd.args[0])[0]
        if isinstance(event, GroupMessageEvent):
            group_map_names[event.group_id] = map_name
        elif isinstance(event, PrivateMessageEvent):
            private_map_names[event.user_id] = map_name

    kz_mode = cd.mode

    content = dedent(f"""
        ╔ 地图:　{map_name}
        ║ 难度:　T{MAP_TIERS.get(map_name, '未知')}
        ║ 模式:　{kz_mode}
        ╠═════存点记录═════
    """).strip()

    try:
        data = await fetch_world_record(map_name, mode=kz_mode, has_tp=True)
        content += dedent(f"""
            ║ {data['steam_id']}
            ║ 昵称:　　{data['player_name']}
            ║ 用时:　　{format_gruntime(data['time'])}
            ║ 存点数:　{data['teleports']}
            ║ 分数:　　{data['points']}
            ║ 服务器:　{data['server_name']}
            ║ {record_format_time(data['created_on'])}""")
    except IndexError:
        content += f"\n╠ 未发现存点记录:"

    content += f"\n╠═════裸跳记录═════"
    try:
        pro = await fetch_world_record(map_name, mode=kz_mode, has_tp=False)
        content += dedent(f"""
            ║ {pro['steam_id']}
            ║ 昵称:　　{pro['player_name']}
            ║ 用时:　　{format_gruntime(pro['time'])}
            ║ 分数:　　{pro['points']}
            ║ 服务器:　{pro['server_name']}
            ╚ {record_format_time(pro['created_on'])}═══
        """)
    except IndexError:
        content += f"\n未发现裸跳记录:"

    combined_message = MessageSegment.image(get_map_img_url(map_name)) + MessageSegment.text(content)
    await wr.send(combined_message)

    if map_name == 'kz_hb_fafnir':
        await wr.send(MessageSegment.record(Path('data/gokz/sound/fafnir.silk')))


@pr.handle()
async def handle_pr(bot: Bot, event: Event, args: Message = CommandArg()):
    cd = CommandData(event, args)
    if cd.error:
        return await pr.finish(cd.error)

    data = await fetch_personal_recent(cd.steamid, cd.mode)

    content = dedent(f"""
        ╔ 地图:　　{data['map_name']}
        ║ 难度:　　T{MAP_TIERS.get(data['map_name'], '未知')}
        ║ 模式:　　{cd.mode}
        ║ 玩家:　　{data['player_name']} 
        ║ 用时:　　{format_gruntime(data['time'])}
        ║ 存点数:　{data['teleports']}
        ║ 分数:　　{data['points']}
        ║ 服务器:　{data['server_name']}
        ╚ {record_format_time(data['created_on'])} ═══""").strip()

    if isinstance(event, GroupMessageEvent):
        group_map_names[event.group_id] = data['map_name']
    elif isinstance(event, PrivateMessageEvent):
        private_map_names[event.user_id] = data['map_name']

    combined_message = MessageSegment.image(get_map_img_url(data['map_name'])) + MessageSegment.text(content)

    await bot.send(event, combined_message)


@pb.handle()
async def map_pb(bot: Bot, event: Event, args: Message = CommandArg()):
    cd = CommandData(event, args)
    if cd.error:
        return await pb.finish(cd.error)

    if not cd.args:
        if isinstance(event, GroupMessageEvent):
            map_name = group_map_names.get(event.group_id, DEFAULT_MAP)
        elif isinstance(event, PrivateMessageEvent):
            map_name = private_map_names.get(event.user_id, DEFAULT_MAP)
        else:
            map_name = DEFAULT_MAP
    else:
        map_name = search_map(cd.args[0])[0]
        if isinstance(event, GroupMessageEvent):
            group_map_names[event.group_id] = map_name
        elif isinstance(event, PrivateMessageEvent):
            private_map_names[event.user_id] = map_name

    content = dedent(f"""
        ╔ 地图:　{map_name}
        ║ 难度:　T{MAP_TIERS.get(map_name, '未知')}
        ║ 模式:　{cd.mode}
        ╠═════存点记录═════""").strip()

    try:
        data = await fetch_personal_best(cd.steamid, map_name, cd.mode)
        if data:
            content += dedent(f"""
                ║ 玩家:　　{data['player_name']}
                ║ 用时:　　{format_gruntime(data['time'])}
                ║ 存点:　　{data['teleports']}
                ║ 分数:　　{data['points']}
                ║ 服务器:　{data['server_name']}
                ║ {record_format_time(data['created_on'])} """)
        else:
            content += f"\n║ 未发现存点记录"
    except Exception as e:
        logger.info(repr(e))
        content += f"\n║ 未发现存点记录"

    content += f"\n╠═════裸跳记录═════"

    try:
        pro = await fetch_personal_best(cd.steamid, map_name, cd.mode, has_tp=False)
        if pro:
            content += dedent(f"""
                ║ 玩家:　　{pro['player_name']}
                ║ 用时:　　{format_gruntime(pro['time'])}
                ║ 分数:　　{pro['points']}
                ║ 服务器:　{pro['server_name']}
                ╚ {record_format_time(pro['created_on'])} ═══""")
        else:
            content += f"\n╚ 未发现裸跳记录"
    except Exception as e:
        logger.info(repr(e))
        content += f"\n╚ 未发现裸跳记录"

    combined_message = MessageSegment.image(get_map_img_url(map_name)) + MessageSegment.text(content)

    await bot.send(event, combined_message)


@kz.handle()
async def handle_kz(bot: Bot, event: Event, args: Message = CommandArg()):
    cd = CommandData(event, args)
    if cd.error:
        return await bot.send(event, cd.error)

    if cd.mode == "kz_vanilla":
        await bot.send(event, "客服小祥正在为您: 生成vnl.kz图片...")
        url = await vnl_screenshot_async(cd.steamid, force_update=cd.update)
    else:
        await bot.send(event, "客服小祥正在为您: 生成kzgo.eu图片...")
        url = await kzgoeu_screenshot_async(cd.steamid, cd.mode, force_update=cd.update)

    image_path = Path(url)
    if image_path.exists():
        await bot.send(event, MessageSegment.image(image_path))
    else:
        await bot.send(event, "图片生成失败，请稍后重试。")

