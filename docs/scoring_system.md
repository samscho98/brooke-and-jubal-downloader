# Scoring System Documentation

## Overview

The scoring system determines the optimal order for playing audio files based on multiple factors including:

- YouTube metadata (views, comments)
- Playback history and user engagement
- Time-of-day effects
- Content freshness

## Scoring Algorithm

The base score for each file is calculated using:

```
base_score = log10(youtube_views) * engagement_boost
engagement_boost = 1 + (youtube_comments / youtube_views)
```

This is then modified by additional factors:

### Freshness Boost

New content receives a boost to ensure it gets exposure:

```
if is_new_release:  // Released in last 14 days
    freshness_bonus = (14 - days_since_release) * 0.1  // Up to +1.4 bonus
    base_score += freshness_bonus
```

### Loyalty Effects

Content that retains listeners receives a boost:

```
loyalty_boost = 1 + (returning_listener_percentage * 0.5)
enhanced_base_score = base_score * loyalty_boost
```

### Time-of-Day Effects

Different content performs better at different times:

```
final_score = enhanced_base_score * time_effects[current_time_slot]```
```

## Queue Generation

The queue manager creates play queues by:

1. Calculating scores for all available content
2. Filtering by any user-selected criteria
3. Applying diversity rules to avoid repetition
4. Sorting by final score (highest first)
5. Optionally injecting high-priority content

## Customization

The scoring system can be customized in `config.ini`:

```ini
[scoring]
enable_scoring = True
score_decay = 0.9        # How quickly scores decay with time
new_content_boost = 1.5  # Boost for new content
time_effect_strength = 1.0 # How strongly time-of-day affects scores
```

## Performance Metrics

The system tracks these metrics to refine scoring:

- Listener retention during playback
- Skip/replay actions
- Time spent listening
- Content that drives engagement

This data is stored in `metrics.json` and used to improve future scoring.