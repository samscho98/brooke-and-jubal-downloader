# Stream Video Scoring System Design

## Objective
To design a dynamic scoring algorithm that determines the optimal order of playing YouTube audio clips during a
livestream. The goal is to maximize viewer engagement and retention by leveraging:
- YouTube metadata (views, comments)
- Livestream performance data (viewer change, chat activity)
- Time of day (with a focus on U.S., U.K., and Philippine audiences)
- Playlist-specific audience preferences
- **Returning viewer data and loyalty metrics** (NEW)

## Data to Gather Per Video

### YouTube Metadata:
- `video_id` (string)
- `title` (string)
- `youtube_views` (int)
- `youtube_comments` (int)
- `video_duration_minutes` (float)
- **`upload_date` (date) — when video was published to YouTube** (NEW)
- **`is_new_release` (boolean) — flag for content published within last 14 days** (NEW)
- **`days_since_release` (int) — number of days since upload** (NEW)

### Livestream Performance:
- `stream_chat_messages` (int) — messages in chat during video play
- `viewer_change` (int) — viewers after video minus viewers before
- `avg_viewers_during_segment` (int)
- `times_played` (int)
- `viewer_retention` (optional, float) — % of viewers who stay post-segment
- **`returning_viewer_count` (int) — number of viewers who have watched previous streams** (NEW)
- **`returning_viewer_percentage` (float) — percentage of total viewers who are returning** (NEW)
- **`returning_viewer_retention` (float) — percentage of returning viewers who stay throughout the segment** (NEW)

### Time Metadata:
- `utc_play_time` (string or timestamp)
- `time_slot_label` (enum: US_PrimeTime, UK_Evening, PH_Evening, etc.)

### Playlist Metadata:
- `playlist_name` (string) — radio show or theme category

## Time Slot Labels (UTC)

| Label | UTC Time Range | Notes |
|-------|----------------|-------|
| US_PrimeTime | 22:00 – 03:00 UTC | 6–11 PM ET |
| UK_Evening | 18:00 – 22:00 UTC | 6–10 PM GMT |
| PH_Evening | 10:00 – 16:00 UTC | 6 PM – 12 AM PHT |
| Low_Traffic | All other times | Ideal for testing |

## Scoring System

### 1. Initial Score (Static Base)
```
base_score = log10(youtube_views) * engagement_boost
engagement_boost = 1 + (youtube_comments / youtube_views)
```

**Example:**
- youtube_views = 500,000
- youtube_comments = 1,200
- engagement_boost = 1 + (1200 / 500000) = 1.0024
- base_score = log10(500000) * 1.0024 ≈ 5.7

#### NEW: New Video Handling
For new or recently released videos with low view counts but high potential:
```
if youtube_views < 10000 and is_new_release:  // Released in last 14 days
    // Provide a "boost" to give new content a fair chance
    min_score = 3.5  // Equivalent to about 3,000+ views
    base_score = max(base_score, min_score)
    
    // Add "freshness bonus" to prioritize newer content
    freshness_bonus = (14 - days_since_release) * 0.1  // Up to +1.4 bonus
    base_score += freshness_bonus
```

This adjustment ensures new videos get fair exposure despite not having accumulated views yet, preventing the algorithm from only selecting older, established content.

### 2. NEW: Loyalty Multiplier
```
loyalty_boost = 1 + (returning_viewer_percentage * 0.5)
enhanced_base_score = base_score * loyalty_boost
```

**Example:**
- returning_viewer_percentage = 0.65 (65% of viewers are returning)
- loyalty_boost = 1 + (0.65 * 0.5) = 1.325
- enhanced_base_score = 5.7 * 1.325 = 7.55

### 3. Time Effect Modifier
Each time slot has an evolving multiplier:
```json
"time_effects": {
  "US_PrimeTime": 1.3,
  "UK_Evening": 1.1,
  "PH_Evening": 0.9
}
```

Final prediction before play:
```
predicted_viewer_change = enhanced_base_score * time_effects[time_slot_label]
```

### 4. NEW: Retention History Parameter
For videos that have been played multiple times:
```python
retention_history = []  // Array of historical retention rates
avg_retention = sum(retention_history) / len(retention_history)
retention_trend = (latest_retention - avg_retention) / avg_retention  // Shows if retention is improving
```

## Post-Play Feedback Loop

### 1. Gather Post-Metrics:
- `actual_viewer_change`
- `stream_chat_messages`
- **`returning_viewer_count`** (NEW)
- **`returning_viewer_retention`** (NEW)

### 2. Score Adjustment:
```
delta = actual_viewer_change - predicted_viewer_change
learning_rate = 0.01
new_score = enhanced_base_score + (learning_rate * delta)
```

### 3. NEW: Returning Viewer Impact Adjustment
```
returning_viewer_impact = 0.8 * returning_viewer_percentage + 0.2 * returning_viewer_retention
adjusted_score = new_score + (learning_rate * returning_viewer_impact)
```

### 4. Engagement Score Update
```
engagement_score = (
  0.6 * (youtube_comments / youtube_views) +
  0.4 * (stream_chat_messages / avg_viewers_during_segment)
)
```

## Playlist-Specific Scoring

### 1. Local and Global Scores
Each episode gets:
- A local score relative to others in its playlist
- A global score across all playlists

### 2. Playlist Metadata & Structure
```json
"playlist": {
  "name": "Morning Madness",
  "historical_avg_change": 130,
  "time_effects": {
    "US_PrimeTime": 1.2,
    "UK_Evening": 0.9
  },
  "episodes": [...],
  "playlist_affinity": {
    "US_PrimeTime": 1.3,
    "PH_Evening": 0.7
  }
}
```

### 3. NEW: Time-Based Loyalty Patterns
Different viewer segments might show different loyalty patterns at different times:
```json
"viewer_segments": {
  "loyal_viewers": {
    "US_PrimeTime": 0.65,  // 65% of US prime time viewers are returning
    "UK_Evening": 0.48,
    "PH_Evening": 0.72
  }
}
```

### 4. Playlist Selection Weight
```
playlist_weight = global_playlist_score * current_time_effect
```

### 5. Cold Start for New Playlists
- Play new shows during off-peak hours
- Use average performance of similar playlists for initialization
- Gradually adjust scores as data accumulates

## NEW: Loyalty-Based Programming Strategy
```
if current_stream_returning_percentage > 0.7:
    // Program more nostalgic or callback content
    preference = "returning_favorites"
else:
    // Program more exploration content
    preference = "new_discoveries"
```

## JSON Structure Example
```json
{
  "video_id": "abc123",
  "title": "Best Segment Ever",
  "playlist_name": "Morning Madness",
  "youtube_views": 502345,
  "youtube_comments": 432,
  "stream_chat_messages": 60,
  "video_duration_minutes": 12,
  "viewer_change": 200,
  "avg_viewers_during_segment": 1000,
  "returning_viewer_count": 650,
  "returning_viewer_percentage": 0.65,
  "returning_viewer_retention": 0.85,
  "times_played": 4,
  "score": 6.12,
  "engagement_score": 1.18,
  "loyalty_score": 0.78,
  "time_effects": {
    "US_PrimeTime": 1.3,
    "UK_Evening": 1.1,
    "PH_Evening": 0.9
  },
  "time_slot_label": "US_PrimeTime"
}
```

## Exploration vs. Exploitation: Testing New Shows

### Objective
Introduce and evaluate new or less-common radio segments without negatively impacting core audience retention.

### Strategy

#### 1. Controlled Exploration
- Play 1 in every 10 segments from a less-known or new playlist.
- Schedule these tests during low or medium traffic periods.
- Inform the audience (if possible) that it's a "special segment" or test.
- **NEW: Include a "new release spotlight" segment in each stream** to ensure fresh content gets exposure regardless of its initial metrics
- **NEW: For promising new videos with few views, use a "potential-based" scoring approach:**
```
potential_score = (engagement_rate * 5000) + freshness_bonus
```
  Where engagement_rate = (youtube_comments / youtube_views) and is typically higher for quality new content even with fewer absolute views

#### 2. NEW: Loyalty-Aware Exploration Rate
```
// If many returning viewers are present
if returning_viewer_percentage > 0.6:
    // Reduce exploration rate slightly to keep familiar content
    exploration_rate = 0.08  // 8% instead of 10%
else:
    // Standard exploration rate
    exploration_rate = 0.1   // 10%
```

#### 3. Exploration Score Adjustment
Expect a drop in viewership, but log actual performance relative to that expectation:
```
expected_drop = 0.85 # assume a 15% drop for unknown shows
adjusted_score = base_score * expected_drop
```
If the segment performs better than this expectation, it earns a higher `exploration_success_score`.

#### 4. Logging Metrics for New Shows
Track for each exploratory segment:
- `viewer_drop_percent`
- `chat_messages_per_minute`
- `viewer_return_rate` (percentage of users who stay or come back after)
- **`returning_viewer_reaction` (how returning viewers respond compared to new viewers)** (NEW)

Use these metrics to compute a potential_growth_score:
```
potential_growth_score += learning_rate * (actual_change - expected_drop)
```

#### 5. Metadata Example
```json
{
  "video_id": "xyz987",
  "playlist_name": "Late Night Laughs",
  "is_exploratory": true,
  "expected_drop": 0.85,
  "actual_viewer_change": -80,
  "returning_viewer_reaction": 0.72,
  "exploration_success_score": 0.43
}
```

#### 6. Gradual Promotion
If a new show starts exceeding expectations:
- Increase its play probability
- Try it in better time slots
- Compare its trend to that of popular shows

This controlled A/B testing ensures the stream remains dynamic and fresh without sacrificing the existing audience base.

## Data Storage Implementation

For local implementation, a JSON-based file structure is recommended:

### File Structure

```
livestream_tracker/
├── data/
│   ├── videos.json        # All video metadata and performance history
│   ├── streams/           # One file per stream session
│   │   ├── stream_2025-05-08.json
│   │   └── stream_2025-05-10.json
│   ├── viewers.json       # Returning viewer tracking
│   ├── playlists.json     # Playlist metadata and performance
│   └── time_effects.json  # Time slot performance data
├── config.json            # Configuration settings
└── tracker.py             # Main Python script
```

## Data Collection During TikTok Livestream

### Essential Data to Collect:

#### Viewer Identity & History Data
- **Unique viewer IDs** - To track who is watching (anonymized if needed)
- **Returning status flags** - Whether each viewer has watched previous streams
- **Viewer history** - How many past streams each viewer has watched
- **First-time viewer count** - Number of new viewers for this stream

#### Real-time Engagement Metrics
- **Stream chat messages** - Total messages during each video segment
- **Viewer count at start of segment** - Baseline before playing each clip
- **Viewer count at end of segment** - To calculate viewer_change
- **Average viewers during segment** - For calculating engagement rates
- **Chat messages per minute** - To normalize chat activity across segments
- **Gift/donation activity** - TikTok-specific engagement through coins, gifts, etc.

#### Viewer Retention Metrics
- **Returning viewer count** - How many previous viewers came back
- **Returning viewer percentage** - What fraction of your audience consists of loyal viewers
- **Returning viewer retention** - How long returning viewers stay compared to new viewers

#### Time-Related Information
- **UTC timestamp** - When each segment plays
- **Time slot label** - Which audience region category this falls into

## Summary

This enhanced system combines static popularity, real-time behavior, time-of-day effects, playlist-specific dynamics, and now returning viewer loyalty metrics to optimize livestream content. It self-adjusts over time, becoming more accurate and reflective of viewer preferences across regions and shows.

The integration of returning viewer data provides a deeper understanding of audience loyalty and allows for more sophisticated content programming strategies that balance familiar content for returning viewers with exploration to attract new audience members.