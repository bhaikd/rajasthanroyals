# Schema Notes & Table Relationships

**Generated during Stage 0 Data Audit**

## Table: `competitions.csv`
- **Dimensions**: 141 rows x 4 columns
- **Columns**: `comp_id, comp_name, match_format, season`
- **Key Identifiers**: `comp_id`

---

## Table: `matches.csv`
- **Dimensions**: 883 rows x 22 columns
- **Columns**: `match_id, comp_id, match_number, match_date, stage, venue_id, venue_country, home_team_id, home_team, away_team_id, away_team, home_team_captain_id, away_team_captain_id, toss_win_team_id, toss_opted, man_of_the_match, first_inn_revised_overs, second_inn_revised_overs, revised_target, knock_out, win_team_id, result`
- **Key Identifiers**: `match_id, comp_id, match_number, venue_id, home_team_id, away_team_id, home_team_captain_id, away_team_captain_id, toss_win_team_id, win_team_id`
- **Date Range**: 2022-01-22 to 2026-11-01

---

## Table: `teams.csv`
- **Dimensions**: 353 rows x 3 columns
- **Columns**: `comp_id, team_id, team_name`
- **Key Identifiers**: `comp_id, team_id`

---

## Table: `playing_eleven.csv`
- **Dimensions**: 28,381 rows x 9 columns
- **Columns**: `match_id, team_id, player_id, batting_order, is_played, is_captain, is_wk, is_impact, is_impact_off`
- **Key Identifiers**: `match_id, team_id, player_id`

---

## Table: `competition_team_player_mapping.csv`
- **Dimensions**: 6,413 rows x 6 columns
- **Columns**: `comp_id, comp_name, team_id, team_name, player_id, player_name`
- **Key Identifiers**: `comp_id, team_id, player_id`

---

## Table: `ball_by_ball.csv`
- **Dimensions**: 200,999 rows x 33 columns
- **Columns**: `match_id, innings, overid, over_ball_num, innings_ball_num, batting_team_id, bowling_team_id, striker_id, striker_name, non_striker_id, non_striker_name, bowler_id, bowler_name, batting_type, bowling_type, batting_order, runs, is_four, is_six, is_wicket, dismissal_type_id, dismissal_type, dismissed_player_id, extras_type, extras1_runs, extras_2_runs, pace_or_spin, bowl_speed, stroke, delivery_style, over_or_around, on_or_off, delivery_ist_time`
- **Key Identifiers**: `match_id, overid, batting_team_id, bowling_team_id, striker_id, non_striker_id, bowler_id, dismissal_type_id, dismissed_player_id`
- **Delivery Time Range**: 2022-01-23 to 2026-11-01

---

## Join Architecture & Entity-Relationship Mapping

1. **matches.csv <-> competitions.csv**:
   - Join Key: `comp_id`
   - Purpose: Connects each match to tournament format (IPL vs T20I) and season.
2. **ball_by_ball.csv <-> matches.csv**:
   - Join Key: `match_id`
   - Purpose: Attaches venue, teams, toss, revised overs (DLS), knockout flag, and winner to deliveries.
3. **ball_by_ball.csv <-> teams.csv**:
   - Join Keys: `batting_team_id` / `bowling_team_id` <-> `team_id`
   - Purpose: Resolves team identities.
4. **ball_by_ball.csv <-> competition_team_player_mapping.csv**:
   - Join Keys: `striker_id` / `bowler_id` / `non_striker_id` <-> `player_id`
   - Purpose: Standardizes canonical player names and teams across tournaments.
5. **playing_eleven.csv <-> matches.csv**:
   - Join Keys: `match_id`, `team_id`, `player_id`
   - Purpose: Tracks starting lineups, batting orders, captaincy, wicketkeepers, and impact player subs.
