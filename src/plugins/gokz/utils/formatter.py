from datetime import datetime

import pytz


def date_to_format(date, delta=False):
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")

    # Convert UTC to GMT+8:00
    if delta:
        gmt8 = pytz.timezone("Asia/Shanghai")
        date = date.replace(tzinfo=pytz.utc).astimezone(gmt8)

    return date.strftime("%Y年%m月%d日 %H:%M")
