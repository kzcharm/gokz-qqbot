import argparse
import shlex
from dataclasses import dataclass, field, asdict

from nonebot.adapters.onebot.v11 import Event, Message
from nonebot.params import CommandArg
from sqlmodel import Session

from ..database.db import engine
from ..database.models import User
from ..utils.kreedz import format_kzmode


@dataclass
class CommandData:
    mode: str
    qid: str
    map_name: str
    steamid: str
    steamid2: str | None = None
    args: tuple = field(default_factory=tuple)
    update: bool = False
    error: str | None = None

    def __init__(self, event: Event, args: Message = CommandArg()):
        self.qid = event.get_user_id()
        parsed_args = parse_args(args.extract_plain_text())

        with Session(engine) as session:
            user: User = session.get(User, self.qid)  # NOQA

            if not user or not user.steamid:
                self.error = '客服小祥温馨提示您: 请先 "/bind steamid"'
                return

            qid = parsed_args.get('qid')
            if qid:
                user2 = session.get(User, qid)
                if not user2 or not user2.steamid:
                    self.error = "你指定的用户未绑定steamid"
                    return
                self.steamid = user2.steamid
                self.steamid2 = user.steamid
            else:
                self.steamid = parsed_args.get('steamid') if parsed_args.get('steamid') else user.steamid
                self.steamid2 = user.steamid if parsed_args.get('steamid') else None

        self.mode = format_kzmode(parsed_args.get('mode', user.mode)) if parsed_args.get('mode') else user.mode
        self.map_name = parsed_args.get('map_name', "")
        self.update = parsed_args.get('update', False)
        self.args = parsed_args.get('args', ())

    def to_dict(self):
        return asdict(self)


def parse_args(text: str) -> dict:
    parser = argparse.ArgumentParser(description='Parse arguments from a text string.')
    parser.add_argument('args', nargs='*', help='Positional arguments before the flags')
    parser.add_argument('-M', '--map_name', type=str, help='Name of the map')
    parser.add_argument('-m', '--mode', type=str, help='KZ模式')
    parser.add_argument('-s', '--steamid', type=str, help='Steam ID')
    parser.add_argument('-q', '--qid', type=str, help='QQ ID')
    parser.add_argument('-u', '--update', action='store_true', help='Update flag')

    args = parser.parse_args(shlex.split(text))
    result = vars(args)
    result['args'] = tuple(result['args'])
    return result
