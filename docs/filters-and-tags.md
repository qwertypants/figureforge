# Filters & Tag Taxonomy

All dimensions are **enums** and **versioned/configurable** (stored in DynamoDB as configuration records).

## Dimensions
- **Pose**: standing, sitting, crouching, jumping, running, lying, foreshortened
- **Body Region**: full_body, torso, head, hands, feet
- **Style**: realistic, comic, anime, silhouette, line_art, low_poly
- **Clothing**: casual, sport, fantasy, robe, armor, sci-fi, anon
- **Lighting**: flat, rim, chiaroscuro, high_key, low_key
- **Camera**: front, side, back, top_down, low_angle, dutch_angle, isometric
- **Theme**: sport, ballet, fantasy, martial_arts, daily_life
- **Background**: minimal, plain_color, gradient

## Auto-Tagging Strategy
- Tags are generated **before** image creation together with the prompt (LLM output).
- They represent a **normalized, consistent schema** (e.g. `pose:standing`).
- These tags feed **TagIndex** items for ultra-fast query/pagination.

## Sorting
- MVP: Mostly recent / curated galleries.
- Future: most_favorited, trending, etc. (store counters on Image).
