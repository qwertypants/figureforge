# Moderation

## Flow
1. User flags an image and selects one or more reasons (enum).
2. Image is immediately hidden from everyone.
3. LLM-based moderation checks whether the flag is valid.
4. If violation confirmed → stays removed, user gets notified.
5. If clean → user can escalate to human admin (image remains hidden until admin resolves).
6. Admin can resolve: `unflag` or `remove`.
7. Log every action in DynamoDB for audit.

## Reasons (enum)
- `nsfw`
- `hate`
- `violence`
- `copyright`
- `privacy`
- `other`

## Data
- `Report` items: `IMG#<image_id> | REPORT#<report_id>`
- `flag_status` on Image: `clean | auto_blocked | human_pending | removed`

## Admin
- Route: `/app/admin/reports`
- Capabilities: list, resolve, view history/audit.
