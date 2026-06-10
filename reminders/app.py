import os

from aiohttp import web

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

REMINDERS = {}
NEXT_ID = 1


def _seed_default() -> None:
    global NEXT_ID
    REMINDERS[NEXT_ID] = {
        'id': NEXT_ID,
        'title': 'Pay credit card statement',
        'completed': False,
    }
    NEXT_ID += 1


_seed_default()


async def list_reminders(request: web.Request) -> web.Response:
    return web.json_response(list(REMINDERS.values()))


async def get_reminder(request: web.Request) -> web.Response:
    reminder_id = int(request.match_info['id'])
    reminder = REMINDERS.get(reminder_id)
    if reminder:
        return web.json_response(reminder)
    return web.json_response({'error': 'Not found'}, status=404)


async def create_reminder(request: web.Request) -> web.Response:
    global NEXT_ID
    data = await request.json()
    reminder = {
        'id': NEXT_ID,
        'title': data.get('title', ''),
        'completed': data.get('completed', False),
    }
    REMINDERS[NEXT_ID] = reminder
    NEXT_ID += 1
    return web.json_response(reminder, status=201)


async def update_reminder(request: web.Request) -> web.Response:
    reminder_id = int(request.match_info['id'])
    if reminder_id not in REMINDERS:
        return web.json_response({'error': 'Not found'}, status=404)
    data = await request.json()
    REMINDERS[reminder_id].update({
        'title': data.get('title', REMINDERS[reminder_id]['title']),
        'completed': data.get('completed', REMINDERS[reminder_id]['completed']),
    })
    return web.json_response(REMINDERS[reminder_id])


async def delete_reminder(request: web.Request) -> web.Response:
    reminder_id = int(request.match_info['id'])
    if reminder_id in REMINDERS:
        del REMINDERS[reminder_id]
        return web.json_response({'status': 'deleted'})
    return web.json_response({'error': 'Not found'}, status=404)


async def health(request: web.Request) -> web.Response:
    return web.json_response({'status': 'ok'})


def create_app() -> web.Application:
    app = web.Application()

    async def redirect_root(request: web.Request) -> web.Response:
        raise web.HTTPFound('/static/index.html')

    app.router.add_routes([
        web.get('/', redirect_root),
        web.static('/static', STATIC_DIR),
        web.get('/health', health),
        web.get('/reminders', list_reminders),
        web.post('/reminders', create_reminder),
        web.get('/reminders/{id}', get_reminder),
        web.put('/reminders/{id}', update_reminder),
        web.delete('/reminders/{id}', delete_reminder),
    ])
    return app


if __name__ == '__main__':
    web.run_app(create_app(), host='0.0.0.0', port=8001)
