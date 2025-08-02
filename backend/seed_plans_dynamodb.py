import boto3
import json

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("figureforge")  # Adjust if your table name differs

with open("pricing.json") as f:
    plans = json.load(f)

for plan in plans:
    item = {
        "pk": f"PLAN#{plan['plan_id']}",
        "sk": "META",
        **plan
    }
    print(f"Seeding plan {plan['plan_id']}...")
    table.put_item(Item=item)

print("✅ DynamoDB seeded with plans from pricing.json")
