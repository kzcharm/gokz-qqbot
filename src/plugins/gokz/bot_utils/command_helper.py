import argparse
import shlex
import re
from dataclasses import dataclass, field, asdict
from typing import Optional, Tuple

from sqlmodel import Session

from ..database.db import engine
from ..database.models import User
from ..utils.kreedz import format_kzmode
from ..utils.steam_user import convert_steamid


@dataclass
class CommandData:
    mode: str
    qid: str
    map_name: str
    steamid: str
    steamid2: Optional[str] = None
    args: Tuple = field(default_factory=tuple)
    update: bool = False
    error: Optional[str] = None

    def __init__(self, event, args):
        self.qid = event.get_user_id()
        parsed_args = parse_args(args.extract_plain_text())
        if 'error' in parsed_args:
            self.error = parsed_args['error']
            print(f"Error during argument parsing: {self.error}")
            return

        with Session(engine) as session:
            user = session.get(User, self.qid)  # NOQA

            if not user or not user.steamid:
                self.error = '客服小祥温馨提示您: 请先 /bind <steamid>'
                print(self.error)
                return

            qid = parsed_args.get('qid')
            if not qid:
                at_msg = event.get_message().copy()
                for segment in at_msg:
                    if segment.type == 'at':
                        qid = segment.data['qq']
                        break

            if qid:
                user2 = session.get(User, qid)
                if not user2 or not user2.steamid:
                    self.error = "你指定的用户未绑定steamid"
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
    steamid64_pattern = re.compile(r"7656119\d{10}")
    steamid_pattern = re.compile(r"STEAM_[0-1]:[0-1]:\d+")

    parser = argparse.ArgumentParser(description='Parse arguments from a text string.')
    parser.add_argument('args', nargs='*', help='Positional arguments before the flags')
    parser.add_argument('-M', '--map_name', type=str, help='Name of the map')
    parser.add_argument('-m', '--mode', type=str, help='KZ模式')
    parser.add_argument('-s', '--steamid', type=str, help='Steam ID')
    parser.add_argument('-q', '--qid', type=str, help='QQ ID')
    parser.add_argument('-u', '--update', action='store_true', help='Update flag')

    try:
        args = shlex.split(text)
        parsed_args = parser.parse_args(args)

        # Search for steamid64 or steamid in the positional arguments
        for arg in parsed_args.args:
            if steamid64_pattern.match(arg):
                parsed_args.steamid = arg  # Treat as steamid64
                break
            elif steamid_pattern.match(arg):
                parsed_args.steamid = convert_steamid(arg, 64)  # Convert to steamid64
                break

        result = vars(parsed_args)
        result['args'] = tuple(result['args'])
        return result

    except argparse.ArgumentError as e:
        return {'error': f'Argument error: {str(e)}'}
    except SystemExit:
        return {'error': f'未指定参数'}
    except Exception as e:
        return {'error': str(e)}