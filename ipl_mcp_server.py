#!/usr/bin/env python3

import sys
import json
import sqlite3
import os
import re

# Configuration - UPDATE THIS PATH TO YOUR ACTUAL DATABASE LOCATION
DB_FILE = "/Users/mayank/ipl-mcp-server/ipl_data.db"

def normalize_question(question):
    """Normalize question by removing punctuation and extra spaces."""
    # Remove punctuation except apostrophes
    normalized = re.sub(r'[^\w\s\']', ' ', question.lower())
    # Replace multiple spaces with single space and strip
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def get_sql_query(question):
    """Map natural language questions to SQL queries with robust matching."""
    # Normalize the input question
    question_normalized = normalize_question(question)
    
    # Define comprehensive query mappings
    query_map = {
        # Basic Match Information
        "show me all matches in the dataset": """
            SELECT match_id, team1, team2, winner, venue, match_date 
            FROM matches ORDER BY match_date DESC LIMIT 20
        """,
        "which team won the most matches": """
            SELECT winner, COUNT(*) as wins FROM matches 
            WHERE winner IS NOT NULL GROUP BY winner 
            ORDER BY wins DESC LIMIT 10
        """,
        "what was the highest total score": """
            SELECT m.match_id, m.team1, m.team2, m.venue, m.match_date,
                   CASE WHEN d.inning = 1 THEN m.team1 ELSE m.team2 END as batting_team,
                   SUM(d.total_runs) as total_score, d.inning
            FROM matches m 
            JOIN deliveries d ON m.match_id = d.match_id 
            GROUP BY d.match_id, d.inning, m.team1, m.team2, m.venue, m.match_date
            ORDER BY total_score DESC LIMIT 10
        """,
        "show matches played in mumbai": """
            SELECT match_id, team1, team2, winner, venue, match_date 
            FROM matches 
            WHERE LOWER(city) LIKE '%mumbai%' OR LOWER(venue) LIKE '%mumbai%'
            ORDER BY match_date DESC
        """,
        
        # Player Performance
        "who scored the most runs across all matches": """
            SELECT batsman as player, 
                   SUM(runs_scored) as total_runs,
                   COUNT(*) as balls_faced,
                   COUNT(DISTINCT match_id) as matches_played,
                   ROUND(CAST(SUM(runs_scored) AS FLOAT) / COUNT(*) * 100, 2) as strike_rate
            FROM deliveries 
            GROUP BY batsman 
            ORDER BY total_runs DESC LIMIT 15
        """,
        "which bowler took the most wickets": """
            SELECT bowler, 
                   COUNT(*) as wickets,
                   COUNT(DISTINCT match_id) as matches_bowled,
                   COUNT(DISTINCT over || '-' || match_id) as overs_bowled
            FROM deliveries 
            WHERE wicket_kind IS NOT NULL AND wicket_kind != '' 
            GROUP BY bowler 
            ORDER BY wickets DESC LIMIT 15
        """,
        "show me virat kohli's batting stats": """
            SELECT batsman as player,
                   SUM(runs_scored) as total_runs,
                   COUNT(*) as balls_faced,
                   COUNT(DISTINCT match_id) as matches_played,
                   ROUND(CAST(SUM(runs_scored) AS FLOAT) / COUNT(*) * 100, 2) as strike_rate
            FROM deliveries 
            WHERE LOWER(batsman) LIKE '%kohli%' 
            GROUP BY batsman
        """,
        "who has the best bowling figures in a single match": """
            SELECT bowler, match_id,
                   COUNT(*) as wickets_in_match,
                   COUNT(DISTINCT over) as overs_bowled,
                   SUM(runs_scored + extra_runs) as runs_conceded
            FROM deliveries 
            WHERE wicket_kind IS NOT NULL AND wicket_kind != ''
            GROUP BY bowler, match_id 
            ORDER BY wickets_in_match DESC, runs_conceded ASC
            LIMIT 15
        """,
        
        # Advanced Analytics
        "what's the average first innings score": """
            SELECT ROUND(AVG(innings_total), 2) as average_first_innings_score,
                   COUNT(*) as total_first_innings,
                   MIN(innings_total) as lowest_score,
                   MAX(innings_total) as highest_score
            FROM (
                SELECT match_id, SUM(total_runs) as innings_total 
                FROM deliveries 
                WHERE inning = 1 
                GROUP BY match_id
            ) first_innings_scores
        """,
        "which venue has the highest scoring matches": """
            SELECT m.venue,
                   COUNT(DISTINCT m.match_id) as matches_played,
                   ROUND(AVG(venue_scores.total_score), 2) as avg_match_total,
                   MAX(venue_scores.total_score) as highest_match_total
            FROM matches m 
            JOIN (
                SELECT match_id, SUM(total_runs) as total_score
                FROM deliveries GROUP BY match_id
            ) venue_scores ON m.match_id = venue_scores.match_id
            GROUP BY m.venue 
            HAVING matches_played >= 3
            ORDER BY avg_match_total DESC LIMIT 10
        """,
        "show me all centuries scored": """
            SELECT d.batsman as player,
                   m.team1, m.team2, m.venue, m.match_date,
                   SUM(d.runs_scored) as runs_scored,
                   COUNT(d.runs_scored) as balls_faced,
                   ROUND(CAST(SUM(d.runs_scored) AS FLOAT) / COUNT(d.runs_scored) * 100, 2) as strike_rate
            FROM deliveries d
            JOIN matches m ON d.match_id = m.match_id
            GROUP BY d.batsman, d.match_id, m.team1, m.team2, m.venue, m.match_date
            HAVING SUM(d.runs_scored) >= 100
            ORDER BY runs_scored DESC
        """,
        
        # Additional useful queries
        "show me the most successful chase targets": """
            SELECT m.match_id, m.team1, m.team2, m.winner, m.venue,
                   first_innings.score as target,
                   second_innings.score as chased_score,
                   (first_innings.score - second_innings.score) as margin
            FROM matches m
            JOIN (SELECT match_id, SUM(total_runs) as score FROM deliveries WHERE inning = 1 GROUP BY match_id) first_innings 
                ON m.match_id = first_innings.match_id
            JOIN (SELECT match_id, SUM(total_runs) as score FROM deliveries WHERE inning = 2 GROUP BY match_id) second_innings 
                ON m.match_id = second_innings.match_id
            WHERE second_innings.score >= first_innings.score
            ORDER BY target DESC LIMIT 15
        """,
        "which team has the best powerplay performance": """
            SELECT 
                CASE WHEN d.inning = 1 THEN m.team1 ELSE m.team2 END as team,
                COUNT(DISTINCT d.match_id) as matches,
                ROUND(AVG(powerplay_runs), 2) as avg_powerplay_runs,
                MAX(powerplay_runs) as best_powerplay
            FROM deliveries d
            JOIN matches m ON d.match_id = m.match_id
            JOIN (
                SELECT match_id, inning, SUM(total_runs) as powerplay_runs
                FROM deliveries 
                WHERE over < 6 
                GROUP BY match_id, inning
            ) pp ON d.match_id = pp.match_id AND d.inning = pp.inning
            GROUP BY team
            ORDER BY avg_powerplay_runs DESC LIMIT 10
        """
    }
    
    # Create normalized versions of all query keys
    normalized_query_map = {normalize_question(key): value for key, value in query_map.items()}
    
    # Try exact normalized match first
    if question_normalized in normalized_query_map:
        return normalized_query_map[question_normalized]
    
    # Enhanced fuzzy matching with key phrases
    key_phrases = {
        "most matches": "which team won the most matches",
        "highest score": "what was the highest total score", 
        "most runs": "who scored the most runs across all matches",
        "most wickets": "which bowler took the most wickets",
        "kohli stats": "show me virat kohli's batting stats",
        "bowling figures": "who has the best bowling figures in a single match",
        "average score": "what's the average first innings score",
        "highest scoring venue": "which venue has the highest scoring matches",
        "centuries": "show me all centuries scored",
        "mumbai matches": "show matches played in mumbai",
        "chase": "show me the most successful chase targets",
        "powerplay": "which team has the best powerplay performance"
    }
    
    # Check for key phrase matches
    for phrase, mapped_question in key_phrases.items():
        if phrase in question_normalized:
            return normalized_query_map[normalize_question(mapped_question)]
    
    # Fallback: Try word-based similarity
    best_match = None
    best_score = 0
    
    for key in normalized_query_map.keys():
        # Calculate simple word overlap score
        question_words = set(question_normalized.split())
        key_words = set(key.split())
        
        if len(question_words) > 0 and len(key_words) > 0:
            overlap = len(question_words.intersection(key_words))
            score = overlap / max(len(question_words), len(key_words))
            
            if score > best_score and score > 0.3:  # Minimum threshold
                best_score = score
                best_match = key
    
    if best_match:
        return normalized_query_map[best_match]
    
    return "SELECT 'Sorry, I could not understand your question. Try asking about matches, teams, players, or statistics.' as response"

def execute_sql_query(sql_query):
    """Execute SQL query and return formatted results."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        
        if not results:
            return "No results found for your query."
        
        # Format as table
        formatted_result = "\n" + " | ".join(column_names) + "\n"
        formatted_result += "-" * len(formatted_result) + "\n"
        
        for row in results[:20]:
            formatted_row = " | ".join(str(cell) if cell is not None else "N/A" for cell in row)
            formatted_result += formatted_row + "\n"
        
        if len(results) > 20:
            formatted_result += f"\n... and {len(results) - 20} more rows"
            
        return formatted_result
        
    except Exception as e:
        return f"Database error: {str(e)}"

def main():
    """Main MCP server loop with proper protocol handling."""
    
    # Keep the server running
    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue
                
            request = json.loads(line)
            request_id = request.get('id')
            method = request.get('method')
            response = None

            if method == 'initialize':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "ipl-cricket-analyzer",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == 'notifications/initialized':
                # Don't respond to notifications, just continue
                continue
            
            elif method == 'tools/list':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [{
                            "name": "query_ipl_data",
                            "description": "Query IPL cricket data using natural language questions",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "question": {
                                        "type": "string",
                                        "description": "Natural language question about IPL data"
                                    }
                                },
                                "required": ["question"]
                            }
                        }]
                    }
                }
            
            elif method == 'tools/call':
                params = request.get('params', {})
                if params.get('name') == 'query_ipl_data':
                    question = params.get('arguments', {}).get('question', '')
                    sql_query = get_sql_query(question)
                    result = execute_sql_query(sql_query)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text", 
                                    "text": result
                                }
                            ]
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": f"Unknown tool: {params.get('name')}"}
                    }
            
            elif method in ['resources/list', 'prompts/list']:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            if response:
                print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id if 'request_id' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
