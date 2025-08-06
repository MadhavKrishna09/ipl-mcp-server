import os
import json
import sqlite3
from pathlib import Path

# --- Configuration ---
DB_FILE = "ipl_data.db"
DATA_DIR = "ipl_data"

def create_database_schema(cursor):
    """Creates a more detailed database schema to answer all query types."""
    cursor.executescript("""
    DROP TABLE IF EXISTS matches;
    DROP TABLE IF EXISTS innings;
    DROP TABLE IF EXISTS deliveries;

    CREATE TABLE matches (
        match_id INTEGER PRIMARY KEY,
        city TEXT,
        venue TEXT,
        match_date TEXT,
        team1 TEXT,
        team2 TEXT,
        toss_winner TEXT,
        toss_decision TEXT,
        winner TEXT,
        result TEXT,
        result_margin INTEGER,
        player_of_match TEXT
    );

    CREATE TABLE innings (
        inning_id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        inning_number INTEGER,
        team_batting TEXT,
        total_runs INTEGER,
        total_wickets INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches (match_id)
    );

    CREATE TABLE deliveries (
        delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
        inning_id INTEGER,
        over INTEGER,
        ball INTEGER,
        batsman TEXT,
        non_striker TEXT,
        bowler TEXT,
        runs_scored INTEGER,
        extra_runs INTEGER,
        total_runs INTEGER,
        is_four INTEGER,
        is_six INTEGER,
        wicket_kind TEXT,
        player_out TEXT,
        FOREIGN KEY (inning_id) REFERENCES innings (inning_id)
    );
    
    CREATE INDEX idx_matches_winner ON matches (winner);
    CREATE INDEX idx_deliveries_batsman ON deliveries (batsman);
    CREATE INDEX idx_deliveries_bowler ON deliveries (bowler);
    """)
    print("Advanced database schema created successfully.")

def load_data():
    """Parses JSON files and inserts data into the new, detailed schema."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    create_database_schema(cursor)

    data_path = Path(DATA_DIR)
    json_files = list(data_path.glob("*.json"))
    
    if not json_files:
        print(f"Error: No JSON files found in '{DATA_DIR}'.")
        return

    print(f"Processing {len(json_files)} files with the new schema...")
    match_id_counter = 0

    for filepath in json_files:
        match_id_counter += 1
        with open(filepath, 'r') as f:
            data = json.load(f)

        info = data.get('info', {})
        teams = info.get('teams', [None, None])
        outcome = info.get('outcome', {})
        by_details = outcome.get('by', {})
        result_key = list(by_details.keys())[0] if by_details else None

        # Insert match data
        cursor.execute("INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            match_id_counter, info.get('city'), info.get('venue'),
            info.get('dates', [None])[0], teams[0], teams[1],
            info.get('toss', {}).get('winner'), info.get('toss', {}).get('decision'),
            outcome.get('winner'), result_key, by_details.get(result_key),
            info.get('player_of_match', [None])[0]
        ))

        # Insert innings and deliveries
        for i, inning_data in enumerate(data.get('innings', [])):
            inning_number = i + 1
            team_batting = inning_data['team']
            
            total_runs_inning = sum(over.get('runs', {}).get('total', 0) for over in inning_data.get('overs', []))
            total_wickets_inning = sum(len(delivery.get('wickets', [])) for over in inning_data.get('overs', []) for delivery in over.get('deliveries', []))

            cursor.execute("INSERT INTO innings (match_id, inning_number, team_batting, total_runs, total_wickets) VALUES (?, ?, ?, ?, ?)",
                           (match_id_counter, inning_number, team_batting, total_runs_inning, total_wickets_inning))
            inning_id = cursor.lastrowid

            for over_data in inning_data.get('overs', []):
                for ball_num, delivery in enumerate(over_data.get('deliveries', [])):
                    runs = delivery.get('runs', {})
                    is_four = 1 if runs.get('batter', 0) == 4 else 0
                    is_six = 1 if runs.get('batter', 0) == 6 else 0
                    
                    # THE FIX: The VALUES clause now has the correct number of placeholders (13).
                    cursor.execute("""
                    INSERT INTO deliveries (inning_id, over, ball, batsman, non_striker, bowler, runs_scored, extra_runs, total_runs, is_four, is_six, wicket_kind, player_out)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        inning_id, over_data.get('over', 0), ball_num + 1,
                        delivery.get('batter'), delivery.get('non_striker'), delivery.get('bowler'),
                        runs.get('batter', 0), runs.get('extras', 0), runs.get('total', 0),
                        is_four, is_six,
                        delivery.get('wickets', [{}])[0].get('kind'),
                        delivery.get('wickets', [{}])[0].get('player_out')
                    ))
    
    conn.commit()
    conn.close()
    print("Advanced data loading complete.")

if __name__ == "__main__":
    load_data()
