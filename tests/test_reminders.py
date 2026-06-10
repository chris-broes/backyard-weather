from aiohttp.test_utils import AioHTTPTestCase

import reminders.app as reminders_app


class ReminderApiTest(AioHTTPTestCase):

    async def get_application(self):
        reminders_app.REMINDERS.clear()
        reminders_app.REMINDERS[1] = {
            'id': 1,
            'title': 'Pay credit card statement',
            'completed': False,
        }
        reminders_app.NEXT_ID = 2
        return reminders_app.create_app()

    async def test_list_reminders(self):
        resp = await self.client.get('/reminders')
        assert resp.status == 200
        data = await resp.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Pay credit card statement'

    async def test_create_and_get_reminder(self):
        resp = await self.client.post('/reminders', json={'title': 'Transfer to savings'})
        assert resp.status == 201
        created = await resp.json()
        resp = await self.client.get(f"/reminders/{created['id']}")
        assert resp.status == 200
        fetched = await resp.json()
        assert fetched['title'] == 'Transfer to savings'
        assert fetched['completed'] is False

    async def test_toggle_completed(self):
        resp = await self.client.put('/reminders/1', json={'completed': True})
        assert resp.status == 200
        updated = await resp.json()
        assert updated['completed'] is True

    async def test_delete_reminder(self):
        resp = await self.client.delete('/reminders/1')
        assert resp.status == 200
        resp = await self.client.get('/reminders/1')
        assert resp.status == 404

    async def test_health(self):
        resp = await self.client.get('/health')
        assert resp.status == 200
