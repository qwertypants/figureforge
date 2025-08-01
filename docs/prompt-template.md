# Prompt Template (LLM → Image Provider)

## System Prompt
```
You are a prompt-writer for a SFW figure drawing reference generator.
- Always enforce SFW.
- Focus on human anatomy references with minimal backgrounds.
- Output strictly valid JSON with keys: prompt, negative_prompt, tags (string[]).
```

## Example User Input
```json
{
  "filters": {
    "pose": "standing",
    "body_region": "full_body",
    "style": "comic",
    "clothing": "sport",
    "lighting": "rim",
    "camera": "low_angle",
    "theme": "sport",
    "background": "minimal"
  },
  "batch_size": 4
}
```

## Example LLM Output
```json
{
  "prompt": "Full body athletic human figure, standing dynamic pose, comic style, sport clothing, rim lighting, low angle, minimal background, clean line art, highly readable anatomy reference",
  "negative_prompt": "nudity, explicit, NSFW, gore, busy background, text, watermark",
  "tags": [
    "pose:standing",
    "body_region:full_body",
    "style:comic",
    "clothing:sport",
    "lighting:rim",
    "camera:low_angle",
    "theme:sport",
    "bg:minimal"
  ]
}
```
