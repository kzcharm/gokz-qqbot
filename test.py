import argparse
import shlex


def parse_args(text: str) -> dict:
    parser = argparse.ArgumentParser(description='Parse arguments from a text string.')
    parser.add_argument('args', nargs='*', help='Positional arguments before the flags')
    parser.add_argument('-M', '--map_name', type=str, help='Name of the map')
    parser.add_argument('-m', '--mode', type=str, help='KZ模式')
    parser.add_argument('-s', '--steamid', type=str, help='Steam ID')
    parser.add_argument('-q', '--qid', type=str, help='QQ ID')
    parser.add_argument('-u', '--update', action='store_true', help='Update flag')

    try:
        args = parser.parse_args(shlex.split(text))
        result = vars(args)
        result['args'] = tuple(result['args'])
        return result
    except argparse.ArgumentError as e:
        return {'error': f'Argument error: {str(e)}'}
    except SystemExit as e:
        return {'error': f'SystemExit: {str(e)}'}
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    text = "-q "
    args = parse_args(text)
    print(args)
