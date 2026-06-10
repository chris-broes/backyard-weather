from aiohttp import web

PRODUCTS = {
    'cashback_card': {
        'name': 'LedgerLine Cashback Card',
        'tagline': '3% back on dining and groceries',
    },
    'high_yield_savings': {
        'name': 'LedgerLine High-Yield Savings',
        'tagline': '4.20% APY, no minimums',
    },
    'subscription_optimizer': {
        'name': 'Subscription Optimizer',
        'tagline': 'Find and cancel unused subscriptions',
    },
    'commuter_card': {
        'name': 'LedgerLine Commuter Card',
        'tagline': '5% back on rideshare and transit',
    },
    'credit_builder': {
        'name': 'Credit Builder Account',
        'tagline': 'Rebuild your balance with guardrails',
    },
    'round_up_investing': {
        'name': 'Round-Up Investing',
        'tagline': 'Invest spare change automatically',
    },
}


def _product(key: str, reason: str) -> dict:
    return {**PRODUCTS[key], 'reason': reason}


def recommend(profile: dict) -> list[dict]:
    balance = float(profile.get('balance', 0))
    totals = {k: float(v) for k, v in profile.get('category_totals', {}).items()}
    subscription_count = int(profile.get('subscription_count', 0))

    recommendations: list[dict] = []

    dining_groceries = totals.get('Dining', 0) + totals.get('Groceries', 0)
    if dining_groceries >= 100:
        recommendations.append(_product(
            'cashback_card',
            f"You spent ${dining_groceries:.2f} on dining and groceries — "
            f"3% back would return ${dining_groceries * 0.03:.2f}.",
        ))

    if balance < 0:
        recommendations.append(_product(
            'credit_builder',
            'Your balance is negative; a structured plan can help you rebuild.',
        ))
    elif balance >= 500:
        recommendations.append(_product(
            'high_yield_savings',
            f"Your ${balance:.2f} balance could earn 4.20% APY instead of sitting idle.",
        ))

    if subscription_count >= 3 or totals.get('Subscriptions', 0) >= 30:
        recommendations.append(_product(
            'subscription_optimizer',
            f"{subscription_count} subscription charges detected — "
            'most members save by trimming at least one.',
        ))

    if totals.get('Transport', 0) >= 50:
        recommendations.append(_product(
            'commuter_card',
            f"${totals['Transport']:.2f} on transport — 5% back adds up fast.",
        ))

    if not recommendations:
        recommendations.append(_product(
            'round_up_investing',
            'Start small: invest spare change from everyday purchases.',
        ))

    return recommendations[:3]


async def get_recommendations(request: web.Request) -> web.Response:
    try:
        profile = await request.json()
    except Exception:
        return web.json_response({'error': 'Invalid JSON body'}, status=400)
    if not isinstance(profile, dict):
        return web.json_response({'error': 'Profile must be an object'}, status=400)
    return web.json_response({'recommendations': recommend(profile)})


async def list_products(request: web.Request) -> web.Response:
    return web.json_response({'products': list(PRODUCTS.values())})


async def health(request: web.Request) -> web.Response:
    return web.json_response({'status': 'ok'})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_routes([
        web.get('/health', health),
        web.get('/products', list_products),
        web.post('/recommendations', get_recommendations),
    ])
    return app


if __name__ == '__main__':
    web.run_app(create_app(), host='0.0.0.0', port=8002)
