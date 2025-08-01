# Feature Flags

Use DynamoDB items:

```
pk: FEATUREFLAG#global
sk: <flag_name>
{
  "value": true|false|any,
  "updated_at": 1234567890
}
```

## Suggested Flags
- `public_gallery_enabled`
- `bedrock_generation_enabled`
- `batch_size_max`
- `free_teaser_limit`
- `moderation_auto_enabled`
- `upsell_threshold_pct`
- `plan_change_enabled`
