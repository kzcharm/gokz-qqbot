
def format_kzmode(mode, form="full") -> int | str:
    """return kz_timer, kz_simple or kz_vanilla in the specified format"""
    mode_mapping = {
        "v": ("kz_vanilla", "vnl", 0),
        "vnl": ("kz_vanilla", "vnl", 0),
        0: ("kz_vanilla", "vnl", 0),
        "0": ("kz_vanilla", "vnl", 0),
        "kz_vanilla": ("kz_vanilla", "vnl", 0),
        "s": ("kz_simple", "skz", 1),
        "skz": ("kz_simple", "skz", 1),
        1: ("kz_simple", "skz", 1),
        "1": ("kz_simple", "skz", 1),
        "kz_simple": ("kz_simple", "skz", 1),
        "k": ("kz_timer", "kzt", 2),
        "kzt": ("kz_timer", "kzt", 2),
        2: ("kz_timer", "kzt", 2),
        "2": ("kz_timer", "kzt", 2),
        "kz_timer": ("kz_timer", "kzt", 2),
    }

    if mode not in mode_mapping:
        raise ValueError("Invalid mode")

    formatted_mode = mode_mapping[mode]

    formats = {
        "full": formatted_mode[0],
        "f": formatted_mode[0],

        "mid": formatted_mode[1],
        "m": formatted_mode[1],

        "num": formatted_mode[2],
        "n": formatted_mode[2],
        "int": formatted_mode[2],
    }

    if form not in formats:
        raise ValueError("Invalid format type")

    return formats[form]


def format_runtime(time: float, cn=False) -> str:
    # Calculate hours, minutes, and seconds
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = round((time - int(time)) * 1000, 3)  # Round to 3 decimal places

    if cn:
        formatted_time = ""
        if hours >= 1:
            formatted_time += f"{int(hours)}小时"
        if minutes >= 1:
            formatted_time += f"{int(minutes)}分"
        formatted_time += f"{int(seconds)}秒{int(milliseconds):03d}"  # Convert milliseconds to int for formatting
    else:
        # Format the time components
        formatted_time = f"{seconds:.3f}"
        if minutes >= 1:
            formatted_time = f"{minutes:02.0f}:{formatted_time}"
        if hours >= 10:
            formatted_time = f"{int(hours):02d}:{formatted_time}"
        elif hours >= 1:
            formatted_time = f"{int(hours)}:{formatted_time}"

    return formatted_time


if __name__ == '__main__':
    print(format_runtime(3700.1, True))
