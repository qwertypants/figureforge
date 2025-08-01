# Queue & Job Pipeline

## Flow
1. `/generate` validates quota → creates GenerationJob (`status=queued`) → enqueue to SQS.
2. Worker Lambda:
   - Generate prompt/tags via LLM (Bedrock).
   - Call fal.ai to generate images (batch <= 4).
   - Save to S3, write Image + TagIndex to DynamoDB.
   - Decrement quota atomically.
   - Update job `status=succeeded` (or `failed`).
3. Client polls `/jobs/:job_id` for completion.

## Reliability
- SQS redrive policy: `maxReceiveCount = 3`, DLQ: `gen-jobs-dlq`.
- Worker timeout: 60–120s.
- Mark job failed if no heartbeat for 5 min (configurable).
