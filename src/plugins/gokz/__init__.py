from pathlib import Path

import nonebot
from nonebot import get_plugin_config
from nonebot import logger
from nonebot.log import default_format
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="gokz",
    description="A Plugin for GOKZ",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
logger.add("error.log", level="ERROR", format=default_format, rotation="1 week")

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)
