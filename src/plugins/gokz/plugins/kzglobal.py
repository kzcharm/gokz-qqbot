from pathlib import Path
from textwrap import dedent

from nonebot import on_command, logger
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment
from nonebot.params import CommandArg

from ..api_call.kztimerglobal import fetch_personal_best, fetch_personal_recent, fetch_world_record
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


global_map = 'bkz_cakewalk'


@wr.handle()
async def _(event: Event, args: Message = CommandArg()):
    cd = CommandData(event, args)
    if cd.error:
        return await wr.finish(cd.error)
    if not cd.args:
        return await wr.finish("🗺地图名都不给我怎么帮你查WR (￣^￣) ")

    map_name = search_map(cd.args[0])[0]
    kz_mode = cd.mode

    content = dedent(f"""
        ╔ 地图:　{map_name}
        ║ 难度:　T{MAP_TIERS[map_name]}
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

    global global_map
    global_map = data['map_name']

    combined_message = MessageSegment.image(get_map_img_url(data['map_name'])) + MessageSegment.text(content)

    await bot.send(event, combined_message)


@pb.handle()
async def map_pb(bot: Bot, event: Event, args: Message = CommandArg()):
    global global_map
    cd = CommandData(event, args)
    if cd.error:
        return await pb.finish(cd.error)

    if not cd.args:
        map_name = global_map
        # return await pb.finish("🗺地图名都不给我怎么帮你查PB (￣^￣) ")
    else:
        map_name = search_map(cd.args[0])[0]
        global_map = map_name

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
