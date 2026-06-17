-- World Cup Prediction System - Database Schema
-- Auto-generated from football_database_sample.sqlite
-- All tables are public sports data (matches, odds, team stats)

CREATE TABLE asian_odds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_name TEXT,
    fid TEXT,
    company TEXT,
    water_home TEXT,
    handicap TEXT,
    water_away TEXT,
    source TEXT DEFAULT '500.com',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE avg_euro_odds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT,
        match_date TEXT,
        match_time TEXT,
        home_team TEXT,
        away_team TEXT,
        avg_win REAL,
        avg_draw REAL,
        avg_loss REAL,
        captured_ts TEXT DEFAULT (datetime('now','+8 hours'))
    );

CREATE TABLE bjdc_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_num TEXT,
    league TEXT,
    home_team TEXT,
    away_team TEXT,
    handicap TEXT,
    home_win_odds TEXT,
    draw_odds TEXT,
    away_win_odds TEXT,
    source TEXT DEFAULT '500.com',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE euro_odds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_name TEXT,
        company TEXT,
        initial_win REAL,
        initial_draw REAL,
        initial_loss REAL,
        current_win REAL,
        current_draw REAL,
        current_loss REAL,
        captured_ts TEXT DEFAULT (datetime('now','+8 hours'))
    );

CREATE TABLE euro_odds_detail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT,
        match_date TEXT,
        company TEXT,
        home_win REAL,
        draw_odds REAL,
        away_win REAL,
        return_rate REAL,
        source TEXT,
        captured_ts TEXT DEFAULT (datetime('now','+8 hours'))
    );

CREATE TABLE historical_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_name TEXT,
    date TEXT,
    tournament TEXT,
    home_team TEXT,
    away_team TEXT,
    score TEXT,
    odds_home TEXT,
    odds_draw TEXT,
    odds_away TEXT,
    kelly_home TEXT,
    kelly_draw TEXT,
    kelly_away TEXT,
    source TEXT DEFAULT '500.com',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE jclq_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_num TEXT,
    league TEXT,
    home_team TEXT,
    away_team TEXT,
    spread TEXT,
    spread_odds_home TEXT,
    spread_odds_away TEXT,
    total_points TEXT,
    total_over TEXT,
    total_under TEXT,
    source TEXT DEFAULT '500.com',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE master_data (
    match_date TEXT,
    group_name TEXT,
    home_team TEXT,
    away_team TEXT,
    round TEXT,
    score TEXT,
    status TEXT,
    
    sp_h REAL, sp_d REAL, sp_a REAL,
    hhad_gl TEXT, hhad_h REAL, hhad_d REAL, hhad_a REAL,
    avg99_h REAL, avg99_d REAL, avg99_a REAL,
    elo_h REAL, elo_a REAL,
    fifa_h INTEGER, fifa_a INTEGER,
    updated_at TEXT,
    PRIMARY KEY (match_date, home_team)
);

CREATE TABLE model_calibration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT,
        predicted_prob REAL,
        actual_outcome INTEGER,
        confidence_band TEXT,
        settled_at TEXT,
        source TEXT DEFAULT 'upgrade_v1'
    , poisson_lambda_home REAL, poisson_lambda_away REAL, poisson_prob_home REAL, poisson_prob_draw REAL, poisson_prob_away REAL, ev_home REAL, ev_draw REAL, ev_away REAL);

CREATE TABLE odds_data (
    match_id INTEGER,
    home_team TEXT,
    away_team TEXT,
    had_h REAL,
    had_d REAL,
    had_a REAL,
    hhad_gl TEXT,
    hhad_h REAL,
    hhad_d REAL,
    hhad_a REAL,
    had_single INTEGER,
    fetch_time TEXT,
    PRIMARY KEY (match_id, fetch_time)
);

CREATE TABLE odds_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT NOT NULL,
        snapshot_type TEXT,
        had_win REAL,
        had_draw REAL,
        had_loss REAL,
        hadn_win REAL,
        hadn_draw REAL,
        hadn_loss REAL,
        asian_handicap REAL,
        asian_home_water REAL,
        asian_away_water REAL,
        timestamp TEXT,
        UNIQUE(match_key, snapshot_type, timestamp)
    );

CREATE TABLE over_under_odds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_key TEXT,
        match_date TEXT,
        company TEXT,
        current_big REAL,
        current_line REAL,
        current_small REAL,
        line_change TEXT,
        initial_big REAL,
        initial_line REAL,
        initial_small REAL,
        captured_ts TEXT DEFAULT (datetime('now','+8 hours'))
    );

CREATE TABLE recent_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT,
    match_date TEXT,
    opponent TEXT,
    score TEXT,
    goals_for INTEGER,
    goals_against INTEGER,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sfc_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_num TEXT,
    home_team TEXT,
    away_team TEXT,
    match_time TEXT,
    odds_home TEXT,
    odds_draw TEXT,
    odds_away TEXT,
    source TEXT DEFAULT '500.com',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE team_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT,
    league TEXT,
    home_venue TEXT,
    coach TEXT,
    avg_goals_scored TEXT,
    avg_goals_conceded TEXT,
    recent_form TEXT,
    source TEXT DEFAULT '500.com',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE team_stats (
    team_name TEXT PRIMARY KEY,
    fifa_ranking INTEGER,
    transfermarkt_value REAL,
    power_rating REAL,
    group_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
, elo_rating REAL, elo_updated REAL);

CREATE TABLE worldcup_odds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    time TEXT,
    home_team TEXT,
    away_team TEXT,
    play_type TEXT,
    rangqiu TEXT,
    odds TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
, true_win REAL, true_draw REAL, true_loss REAL, overround REAL, bookmaker_count REAL, asian_handicap_mean REAL, asian_water_home REAL, asian_water_away REAL, asian_std REAL);

CREATE TABLE worldcup_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT,
    home_team TEXT,
    away_team TEXT,
    match_time TEXT DEFAULT '',
    score TEXT DEFAULT '',
    status TEXT DEFAULT 'upcoming',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE worldcup_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT UNIQUE,
    group_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
, elo_rating REAL);

