#!/usr/bin/env python
import boto3
import json
import os
import sys
from pathlib import Path
from botocore.exceptions import BotoCore3Error, ClientError

# Add Django project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'figureforge.settings')
import django
django.setup()

from django.conf import settings

# Initialize DynamoDB
try:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    )
    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    table = dynamodb.Table(table_name)
    print(f"Connected to DynamoDB table: {table_name}")
except Exception as e:
    print(f"Error connecting to DynamoDB: {e}")
    print("Make sure AWS credentials and region are properly configured")
    sys.exit(1)

# Load pricing data
pricing_file = Path(__file__).parent / "pricing.json"
if not pricing_file.exists():
    print(f"Error: {pricing_file} not found")
    sys.exit(1)

try:
    with open(pricing_file) as f:
        plans = json.load(f)
    print(f"Loaded {len(plans)} plans from pricing.json")
except Exception as e:
    print(f"Error reading pricing.json: {e}")
    sys.exit(1)

# Confirmation prompt
print("\nThis will seed the following plans to DynamoDB:")
for plan in plans:
    print(f"  - {plan['name']} ({plan['plan_id']}): ${plan['price_usd_month']}/month, {plan['images_per_month']} images")

response = input("\nProceed with seeding? (yes/no): ")
if response.lower() != 'yes':
    print("Seeding cancelled.")
    sys.exit(0)

# Check for existing plans
print("\nChecking for existing plans...")
existing_plans = []
try:
    response = table.query(
        KeyConditionExpression='pk = :pk',
        ExpressionAttributeValues={':pk': 'PLAN#'}
    )
    existing_plans = response.get('Items', [])
    if existing_plans:
        print(f"Found {len(existing_plans)} existing plans in DynamoDB")
        overwrite = input("Overwrite existing plans? (yes/no): ")
        if overwrite.lower() != 'yes':
            print("Seeding cancelled.")
            sys.exit(0)
except ClientError as e:
    # Query might fail if no PLAN# items exist yet
    pass

# Seed plans
print("\nSeeding plans...")
success_count = 0
for plan in plans:
    try:
        item = {
            "pk": f"PLAN#{plan['plan_id']}",
            "sk": "META",
            "plan_id": plan['plan_id'],
            "name": plan['name'],
            "price_usd_month": plan['price_usd_month'],
            "stripe_price_id": plan['stripe_price_id'],
            "images_per_month": plan['images_per_month'],
            "batch_cap": plan['batch_cap'],
            "upsell_threshold_pct": plan['upsell_threshold_pct'],
            "active": plan['active'],
            "created_at": str(django.utils.timezone.now()),
            "updated_at": str(django.utils.timezone.now())
        }
        print(f"  Seeding plan {plan['plan_id']}...")
        table.put_item(Item=item)
        success_count += 1
    except ClientError as e:
        print(f"  Error seeding {plan['plan_id']}: {e}")
    except Exception as e:
        print(f"  Unexpected error seeding {plan['plan_id']}: {e}")

if success_count == len(plans):
    print(f"\n✅ Successfully seeded {success_count} plans to DynamoDB")
else:
    print(f"\n⚠️  Seeded {success_count}/{len(plans)} plans (some errors occurred)")
    sys.exit(1)
