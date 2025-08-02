
# views/pricing.py (Django REST)

from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

@api_view(["GET"])
def get_pricing(request):
    with open("pricing.json") as f:
        plans = json.load(f)
    return Response([
        {k: v for k, v in plan.items() if k != "stripe_price_id"}
        for plan in plans if plan["active"]
    ])
