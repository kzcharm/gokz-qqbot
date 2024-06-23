from textwrap import dedent

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from nonebot.params import CommandArg
from sqlmodel import Session

from ..database.db import engine, create_db_and_tables
from ..database.models import User, Leaderboard
from ..utils.steam_user import conv_steamid


create_db_and_tables()


bind = on_command("bind", aliases={"绑定"})
mode = on_command("mode", aliases={"模式"})
kz = on_command("kz")
test = on_command("test")


@bind.handle()
async def bind_steamid(bot: Bot, event: Event, args: Message = CommandArg()):
    if steamid := args.extract_plain_text():
        try:
            steamid = conv_steamid(steamid)
        except ValueError:
            return await bind.finish("Steamid格式不正确")
    else:
        return await bind.finish("请输steamid")

    # 查找用户是不是玩KZ的
    with Session(engine) as session:
        rank: Leaderboard = session.get(Leaderboard, steamid)  # NOQA
        if not rank:
            return await bind.finish("用户不存在. 你至少上传过一次KZT的记录吗?")

    user_id = event.get_user_id()
    qq_info = await bot.call_api("get_stranger_info", user_id=user_id)
    qq_name = qq_info.get("nickname", 'Unknown')
    user = User(qqid=int(user_id), name=qq_name, steamid=steamid)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    content = dedent(f"""
    绑定成功!
    QQ号: {user.qqid}
    Steamid: {user.steamid}
    昵称: {rank.name}
    段位: {rank.rank_name}
    Rating: {rank.pts_skill}
    总分: {rank.total_points:,}
    """).strip()

    await bind.finish(content)


@kz.handle()
async def reply_im_kz(event: Event):
    qid = event.get_user_id()
    with Session(engine) as session:
        user: User = session.get(User, qid)  # NOQA
        if not user:
            return await kz.finish("请先绑定steamid")

        info: Leaderboard = session.get(Leaderboard, user.steamid)  # NOQA

    content = dedent(f"""
            昵称: {info.name}
            Steamid: {info.steamid}
            段位: {info.rank_name}
            Rating: {info.pts_skill}
            总分: {info.total_points:,}
            均分: {info.pts_avg}
        """).strip()
    await kz.finish(content)


@test.handle()
async def handle_first_receive(bot: Bot, event: Event):
    user_id = event.get_user_id()
    user_info = await bot.call_api("get_stranger_info", user_id=user_id)
    user_name = user_info.get("nickname", 'Unknown')
    await test.finish(f"你的QQ号是：{user_id}, 你的昵称是{user_name}")
