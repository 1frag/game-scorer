import asyncio
import typing
import aiohttp
import dataclasses
import json
import re
import os
import enum

from aiohttp import web

PORT = 9000


async def view_handler(request):
    return web.Response(
        body=open('./view.html').read(),
        content_type='text/html'
    )


async def setter_handler(request):
    return web.Response(
        body=open('./setter.html').read(),
        content_type='text/html'
    )


class Side(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'


INIT_SCORE = 100

@dataclasses.dataclass
class State:
    score: int = INIT_SCORE
    color: str = 'red'


GAME = {
    Side.LEFT: State(),
    Side.RIGHT: State(),
}


class Step(typing.NamedTuple):
    color: str
    sign: str
    score: int


HISTORY: typing.List[Step] = []


async def set_handler(request):
    req = await request.json()
    cur = Side(req['side'])
    op = Side.RIGHT if cur == Side.LEFT else Side.LEFT
    GAME[cur].color = req['color']

    score = int(req['score'])
    HISTORY.append(Step(
        color=GAME[cur].color,
        sign=req['sign'],
        score=score,
    ))
    if req['sign'] == '-':
        GAME[op].score -= score
    else:
        GAME[cur].score += score

    return web.json_response({})


async def data_handler(request):
    res = {}
    for side, value in GAME.items():
        res[side.value] = dataclasses.asdict(value)
    res['history'] = []
    for item in HISTORY:
        res['history'].append({
            'sign': item.sign,
            'score': item.score,
            'color': item.color,
        })
    return web.json_response(res)


async def on_startup(app):
    try:
        host = re.compile('[\d.]+/24').findall(os.popen('ip a | grep /24').read())[0][:-3]
        url = f'http://{host}:{PORT}'
        print(f'\nOpen {url}/v and let {url}/s for others\n')
    except Exception as e:
        print('failed to get address', e)


def main():
    app = web.Application()
    app.router.add_route('GET', '/v', view_handler)
    app.router.add_route('GET', '/s', setter_handler)
    app.router.add_route('POST', '/set', set_handler)
    app.router.add_route('GET', '/data', data_handler)
    app.on_startup.append(on_startup)
    web.run_app(app, port=PORT)


if __name__ == '__main__':
    main()
