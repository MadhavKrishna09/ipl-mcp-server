-- This script creates the tables for the IPL data analysis project.
-- It is designed to be run on an SQLite database.

-- Drop tables if they already exist to ensure a fresh start.
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS deliveries;

-- Create the 'matches' table to store high-level information about each match.
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    city TEXT,
    venue TEXT,
    match_date DATE,
    team1 TEXT,
    team2 TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    winner TEXT,
    result TEXT,
    result_margin INTEGER,
    player_of_match TEXT
);

-- Create the 'deliveries' table for ball-by-ball data.
CREATE TABLE deliveries (
    delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    inning INTEGER,
    over INTEGER,
    ball INTEGER,
    batsman TEXT,
    non_striker TEXT,
    bowler TEXT,
    runs_scored INTEGER,
    extra_runs INTEGER,
    total_runs INTEGER,
    wicket_kind TEXT,
    player_out TEXT,
    FOREIGN KEY (match_id) REFERENCES matches (match_id)
);

-- Create indexes for faster queries.
CREATE INDEX idx_matches_winner ON matches (winner);
CREATE INDEX idx_matches_venue ON matches (venue);
CREATE INDEX idx_deliveries_batsman ON deliveries (batsman);
CREATE INDEX idx_deliveries_bowler ON deliveries (bowler);
CREATE INDEX idx_deliveries_match_id ON deliveries (match_id);