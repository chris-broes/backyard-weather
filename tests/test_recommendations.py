from aiohttp.test_utils import AioHTTPTestCase

from recommendations.app import create_app, recommend


def test_heavy_dining_gets_cashback_card():
    recs = recommend({'balance': 200, 'category_totals': {'Dining': 150.0}})
    assert any('Cashback' in rec['name'] for rec in recs)


def test_large_balance_gets_high_yield_savings():
    recs = recommend({'balance': 1200, 'category_totals': {}})
    assert any('High-Yield' in rec['name'] for rec in recs)


def test_negative_balance_gets_credit_builder():
    recs = recommend({'balance': -50, 'category_totals': {}})
    assert any('Credit Builder' in rec['name'] for rec in recs)


def test_empty_profile_gets_round_up_default():
    recs = recommend({})
    assert len(recs) == 1
    assert 'Round-Up' in recs[0]['name']


def test_caps_at_three():
    recs = recommend({
        'balance': 1000,
        'category_totals': {'Dining': 200, 'Transport': 80, 'Subscriptions': 45},
        'subscription_count': 4,
    })
    assert len(recs) == 3


class RecommendationsApiTest(AioHTTPTestCase):

    async def get_application(self):
        return create_app()

    async def test_health(self):
        resp = await self.client.get('/health')
        assert resp.status == 200

    async def test_products_listed(self):
        resp = await self.client.get('/products')
        assert resp.status == 200
        data = await resp.json()
        assert len(data['products']) >= 5

    async def test_recommendations_endpoint(self):
        resp = await self.client.post('/recommendations', json={
            'balance': 800,
            'category_totals': {'Dining': 120.0},
            'subscription_count': 0,
        })
        assert resp.status == 200
        data = await resp.json()
        names = [rec['name'] for rec in data['recommendations']]
        assert any('Cashback' in name for name in names)
        assert any('High-Yield' in name for name in names)

    async def test_rejects_invalid_body(self):
        resp = await self.client.post('/recommendations', data=b'not json')
        assert resp.status == 400
