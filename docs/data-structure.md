# Data Structure (DynamoDB + S3)

Single-table DynamoDB: **`figureforge`**

## Entities (logical)
- **User**
- **Subscription**
- **GenerationJob**
- **Image**
- **TagIndex** (for fast tag-based search)
- **Report** (moderation)
- **FeatureFlag**
- **Plan**

## Primary Keys
Use `{ pk, sk }` with semantic prefixes:

| Entity | pk | sk |
|-------|----|----|
| User | `USER#<user_id>` | `PROFILE` |
| Subscription | `USER#<user_id>` | `SUB#<stripe_sub_id>` |
| GenerationJob | `USER#<user_id>` | `JOB#<job_id>` |
| Image | `IMG#<image_id>` | `META` |
| TagIndex | `TAG#<tag_value>` | `IMG#<image_id>` |
| Report | `IMG#<image_id>` | `REPORT#<report_id>` |
| FeatureFlag | `FEATUREFLAG#global` | `<flag_name>` |
| Plan | `PLAN#<plan_id>` | `META` |

Use **GSIs** for:
- `byEmail` (PK: `EMAIL#<email>`, SK: `USER#<user_id>`)
- `byStripeSub` (PK: `SUB#<stripe_sub_id>`, SK: `USER#<user_id>`)
- `jobsByStatus` (PK: `JOBSTATUS#<status>`, SK: `created_at`)
- `imagesByUser` (PK: `USER#<user_id>`, SK: `created_at`)
- `reportsByStatus` (PK: `REPORTSTATUS#<status>`, SK: `created_at`)
- `plansByActive`

All items include:
- `created_at` (epoch seconds)
- `deleted_at` (nullable) for soft-delete

### Image Item Example
```json
{
  "pk": "IMG#<uuid>",
  "sk": "META",
  "user_id": "<uuid|null>",
  "url": "https://cdn/.../img.jpg",
  "tags": ["pose:standing", "style:comic", "..."],
  "prompt_json": { "prompt": "...", "negative_prompt": "...", "tags": ["..."] },
  "provider": "fal.ai",
  "provider_model_id": "fal/sdxl-foo",
  "cost_cents": 12,
  "favorited_count": 0,
  "public": true,
  "private_gallery_ids": [],
  "flag_status": "clean|auto_blocked|human_pending|removed",
  "created_at": 1710000000,
  "deleted_at": null
}
```

### Tag Index Item
```json
{
  "pk": "TAG#pose:standing",
  "sk": "IMG#<image_id>",
  "created_at": 1710000000
}
```

## S3 Layout
```
s3://figureforge-prod/
  users/<user_id>/yyyy/mm/dd/<image_uuid>.jpg
  public/teaser/<image_uuid>.jpg
```

Signed-URL TTL default: **10 minutes** (configurable).
