# Stream Video Scoring System Design

## Objective

To design a dynamic scoring algorithm that determines the optimal order of playing YouTube audio clips during a livestream. The goal is to maximize viewer engagement and retention by leveraging:

* YouTube metadata (views, comments)
* Livestream performance data (viewer change, chat activity)
* Time of day (with a focus on U.S., U.K., and Philippine audiences)

---

## Data to Gather Per Video

Each video should include the following fields:

### YouTube Metadata:

* `video_id` (string)
* `title` (string)
* `youtube_views` (int)
* `youtube_comments` (int)
* `video_duration_minutes` (float)

### Livestream Performance:

* `stream_chat_messages` (int) — messages in chat during video play
* `viewer_change` (int) — viewers after video minus viewers before
* `avg_viewers_during_segment` (int)
* `times_played` (int)
* `viewer_retention` (optional, float) — % of viewers who stay post-segment

### Time Metadata:

* `utc_play_time` (string or timestamp)
* `time_slot_label` (enum: US\_PrimeTime, UK\_Evening, PH\_Evening, etc.)

---

## Time Slot Labels (UTC)

| Label         | UTC Time Range    | Notes             |
| ------------- | ----------------- | ----------------- |
| US\_PrimeTime | 22:00 – 03:00 UTC | 6–11 PM ET        |
| UK\_Evening   | 18:00 – 22:00 UTC | 6–10 PM GMT       |
| PH\_Evening   | 10:00 – 16:00 UTC | 6 PM – 12 AM PHT  |
| Low\_Traffic  | All other times   | Ideal for testing |

---

## Scoring System

### 1. Initial Score (Static Base)

```python
base_score = log10(youtube_views) * engagement_boost
engagement_boost = 1 + (youtube_comments / youtube_views)
```

*Example:*

* `youtube_views = 500,000`
* `youtube_comments = 1,200`
* `engagement_boost = 1 + (1200 / 500000) = 1.0024`
* `base_score = log10(500000) * 1.0024 ≈ 5.7`

### 2. Time Effect Modifier

Each time slot has an evolving multiplier:

```json
"time_effects": {
  "US_PrimeTime": 1.3,
  "UK_Evening": 1.1,
  "PH_Evening": 0.9
}
```

Final prediction before play:

```python
predicted_viewer_change = base_score * time_effects[time_slot_label]
```

---

## Post-Play Feedback Loop

### 1. Gather Post-Metrics:

* `actual_viewer_change`
* `stream_chat_messages`

### 2. Score Adjustment:

```python
delta = actual_viewer_change - predicted_viewer_change
learning_rate = 0.01
new_score = base_score + (learning_rate * delta)
```

* Clamp large changes to avoid instability.
* Optionally update `time_effects[time_slot_label]` if many similar deltas occur.

### 3. Engagement Score Update

```python
engagement_score = (
    0.6 * (youtube_comments / youtube_views) +
    0.4 * (stream_chat_messages / avg_viewers_during_segment)
)
```

---

## JSON Structure Example

```json
{
  "video_id": "abc123",
  "title": "Best Segment Ever",
  "youtube_views": 502345,
  "youtube_comments": 432,
  "stream_chat_messages": 60,
  "video_duration_minutes": 12,
  "viewer_change": 200,
  "avg_viewers_during_segment": 1000,
  "times_played": 4,
  "score": 5.73,
  "engagement_score": 1.18,
  "time_effects": {
    "US_PrimeTime": 1.3,
    "UK_Evening": 1.1,
    "PH_Evening": 0.9
  },
  "time_slot_label": "US_PrimeTime"
}
```

---

## Summary

This system combines static popularity, real-time behavior, and contextual time-of-day effects to continually optimize stream content. With enough data, it becomes self-improving and adapts to shifts in audience preference and regional behavior.

Ideal next steps:

* Build a logging pipeline per stream segment
* Establish time zone label detection from UTC
* Implement basic scoring and feedback logic in Python
