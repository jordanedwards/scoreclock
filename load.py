import json
import os
import sqlite3
import requests
from dotenv import load_dotenv
# import horn_and_light

TEAM_LIST_URL = "https://api.nhle.com/stats/rest/en/team"
SCOREBOARD_URL = "https://api-web.nhle.com/v1/scoreboard/tor/now"
BOX_SCORE_URL = "https://api-web.nhle.com/v1/gamecenter/game_id/boxscore"
PLAYERS_URL = "https://api-web.nhle.com/v1/roster/tor/20242025"

DB_FILE = 'scoreclock.db'

def setup_db():
    conn = sqlite3.connect('scoreclock.db')
    # cursor = conn.cursor()
    # Create teams table
    conn.execute('''CREATE TABLE IF NOT EXISTS teams(
    id INTEGER,
    franchiseId INTEGER,
    fullName TEXT,
    triCode TEXT,
    logoLink TEXT);''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS TeamId ON teams (id)  ''')

    # Create schedule table
    # https://www.postman.com/telecoms-participant-38756299/nhl-api/request/6bcqoi1/team-schedule?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
    conn.execute('''CREATE TABLE IF NOT EXISTS schedule(
    id INTEGER,
    season INTEGER,
    gameType INTEGER,
    gameDate TEXT,
    gameCenterLink TEXT,
    venue TEXT,
    startTimeUTC TEXT,
    gameState INTEGER,
    awayTeamId INTEGER,
    awayTeamScore INTEGER,
    homeTeamId INTEGER,
    homeTeamScore INTEGER,
    threeMinRecap TEXT);''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS ScheduleId ON schedule (id)  ''')

    # Create boxscore table
    # https://www.postman.com/telecoms-participant-38756299/nhl-api/example/17726769-4c903f06-9dfb-4dbd-b4dc-a8a044948120?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
    conn.execute('''CREATE TABLE IF NOT EXISTS box_score(
    id INTEGER,
    period INTEGER,
    periodType TEXT,
    timeRemaining TEXT,
    secondsRemaining INTEGER,
    running BOOL,
    inIntermission BOOL,
    awayTeamScore INTEGER,
    awayTeamSOG INTEGER,
    awayTeamPIM INTEGER,
    awayTeamHits INTEGER,
    awayTeamFaceoffWin REAL,
    homeTeamScore INTEGER,
    homeTeamSOG INTEGER,
    homeTeamPIM INTEGER,
    homeTeamHits INTEGER,
    homeTeamFaceoffWin REAL);''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS BoxScoreId ON box_score (id)  ''')

    # Create players table
    # https://www.postman.com/telecoms-participant-38756299/nhl-api/example/17726769-8e43a4e4-0b2c-4d29-8ff0-de26ba54e01e?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
    conn.execute('''CREATE TABLE IF NOT EXISTS players(
    playerId INTEGER,
    currentTeamId INTEGER,
    firstName TEXT,
    lastName TEXT,
    position TEXT,
    sweaterNumber INTEGER,
    headshot TEXT,
    heroImage TEXT
    );''')

    conn.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS PlayersPlayerId ON players (playerId)  ''')
    conn.close()


def retrieve_row(table_name, row_id):
    """Retrieves a specific row from an SQLite database table.

    Args:
        table_name (str): Name of the table to retrieve from.
        row_id: The row ID (primary key) of the row to retrieve.

    Returns:
        tuple: A tuple representing the retrieved row, or None if not found.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # Enable access by column name
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name} WHERE id=?", (row_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)  # Convert sqlite3.Row to a dictionary
        else:
            return None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()


# Example usage:
# table_name = "employees"
# column_updates = {"salary": 60000, "department": "Marketing"}
# row_id = 1
# condition_column = "id"
def update_data(table_name, column_updates, row_id, condition_column = 'id'):
    """
    Updates a row in a SQLite database table.

    Args:
        db_file (str): Path to the SQLite database file.
        table_name (str): Name of the table to update.
        column_updates (dict): Dictionary of column names and their new values.
        condition_column (str): Name of the column to use in the WHERE clause.
        condition_value: Value to match in the WHERE clause.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        update_query = f"UPDATE {table_name} SET "
        update_query += ", ".join([f"{col} = ?" for col in column_updates])
        update_query += f" WHERE {condition_column} = ?"

        values = list(column_updates.values())
        values.append(row_id)

        cursor.execute(update_query, values)
        conn.commit()

        print(f"Row updated successfully in table '{table_name}'.")

    except sqlite3.Error as e:
        print(f"Error updating row: {e}")
    finally:
        if conn:
            conn.close()


# https://www.postman.com/telecoms-participant-38756299/nhl-api/request/s66qexc/team-list?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
def load_teams():
    conn = sqlite3.connect(DB_FILE)
    api_response = requests.get(
        TEAM_LIST_URL,
    )
    api_response.raise_for_status()
    payload = api_response.json()
    # print(payload)

    # Insert each row; skip duplicates using INSERT OR IGNORE
    for team in payload['data']:
        # print(team)
        columns = "id, franchiseId, fullName, triCode"
        placeholders = "?, ?, ?, ?"
        values = [team['id'], team['franchiseId'], team['fullName'], team['triCode']]

        query = f"INSERT OR IGNORE INTO teams ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

        conn.commit()
    conn.close()


def lists_to_dict(keys, values):
    if not keys or not values or len(keys) != len(values):
        print("keys and values not the same length")
        return {}
    output = {}
    i = 0
    for key in keys:
        if i > len(values):
            print("Index out of range")
            return output
        else:
            try:
                output[key] = values[i]
                i = i+1
            except IndexError:
                print("Index is out of range. Please check your list.")
                print(i)

    return output


def load_team_scoreboard():
    print("Loading scoreboard")
    load_dotenv()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    api_response = requests.get(
        SCOREBOARD_URL,
    )
    api_response.raise_for_status()
    payload = api_response.json()
    # print(payload)

    # Insert each row; skip duplicates using INSERT OR IGNORE
    for games in payload['gamesByDate']:
        # print(games)
        record = games["games"][0]
        columns = "id,season,gameType,gameDate,gameCenterLink,venue,startTimeUTC,gameState,awayTeamId,awayTeamScore,homeTeamId,homeTeamScore,threeMinRecap"
        placeholders = "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"

        try:
            threeMinRecap = record['threeMinRecap']
        except KeyError:
            record['threeMinRecap'] = ''
        try:
            score = record['awayTeam']['score']
        except KeyError:
            record['awayTeam']['score'] = 0
            record['homeTeam']['score'] = 0

        # gameState can be "FUT" = future, or "OFF" = finished
        if record["gameState"] == "OFF":
            game_state = 0
        else:
            game_state = 1

        values = [record['id'], record['season'], record['gameType'], record['gameDate'], record['gameCenterLink'],
                  record['venue']['default'], record['startTimeUTC'], game_state, record['awayTeam']['id'],
                  record['awayTeam']['score'], record['homeTeam']['id'], record['homeTeam']['score'],
                  record['threeMinRecap']]

        # Check if the record exists based on the key column
        cursor.execute(f"SELECT 1 FROM schedule WHERE id = " + str(record['id']))
        existing_record = cursor.fetchone()

        if existing_record:
            data = lists_to_dict(columns.split(','), values)
            # Update the existing record
            update_query = f"UPDATE schedule SET "
            update_query += ", ".join([f"{col} = ?" for col in data if col != "id"])
            update_query += f" WHERE id = ?"
            update_values = [data[col] for col in data if col != "id"] + [data["id"]]
            cursor.execute(update_query, update_values)
        else:
            query = f"INSERT OR IGNORE INTO schedule ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)

        conn.commit()
    conn.close()


# https://www.postman.com/telecoms-participant-38756299/nhl-api/request/s66qexc/team-list?action=share&source=copy-link&creator=17590512&active-environment=5fb916f5-4f2b-4470-a9c2-852c88d2b63d
def load_players():
    conn = sqlite3.connect('scoreclock.db')
    api_response = requests.get(
        PLAYERS_URL,
    )
    api_response.raise_for_status()
    payload = api_response.json()
    placeholders = "?, ?, ?, ?, ?, ?, ?"

    for player in payload['forwards']:
        columns = "playerId, currentTeamId, firstName, lastName, position, sweaterNumber, headshot"
        values = [player['id'], '', player['firstName']['default'], player['lastName']['default'],
                  player['positionCode'], player['sweaterNumber'], player['headshot']]
        query = f"INSERT OR IGNORE INTO players ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

    for player in payload['defensemen']:
        columns = "playerId, currentTeamId, firstName, lastName, position, sweaterNumber, headshot"
        values = [player['id'], '', player['firstName']['default'], player['lastName']['default'],
                  player['positionCode'], player['sweaterNumber'], player['headshot']]
        query = f"INSERT OR IGNORE INTO players ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

    for player in payload['goalies']:
        columns = "playerId, currentTeamId, firstName, lastName, position, sweaterNumber, headshot"
        values = [player['id'], '', player['firstName']['default'], player['lastName']['default'],
                  player['positionCode'], player['sweaterNumber'], player['headshot']]
        query = f"INSERT OR IGNORE INTO players ({columns}) VALUES ({placeholders})"
        conn.execute(query, values)

        conn.commit()
    conn.close()


def load_box_score(game_id):
    conn = sqlite3.connect(DB_FILE)
    URL = BOX_SCORE_URL.replace("game_id", str(game_id))
    api_response = requests.get(
        URL,
    )
    api_response.raise_for_status()
    payload = api_response.json()
    # print(payload)

    # Get the score:
    try:
        away_team_score = payload["awayTeam"]["score"]
    except KeyError:
        away_team_score = 0
    try:
        home_team_score = payload["homeTeam"]["score"]
    except KeyError:
        home_team_score = 0

    # Todo: return clock time remaining so that the script knows when to stop

    # Check if the score has changed:
    row = retrieve_row("schedule", game_id)

    print(row)
    # check to see that the game is still running
    if payload["gameState"] == "OFF":
        game_state = 0
    else:
        game_state = 1

    last_away_team_score = row["awayTeamScore"]
    last_home_team_score = row["homeTeamScore"]
    last_game_state = row["gameState"]

    column_updates = {"awayTeamScore": away_team_score, "homeTeamScore": home_team_score, "gameState": game_state}

    if last_away_team_score < away_team_score:
        print("Away team scored!")
        update_data("schedule", column_updates, game_id)

    if last_home_team_score < home_team_score:
        print("Home team scored!")
        update_data("schedule", column_updates, game_id)
        horn_and_light.play()

    if last_game_state != game_state:
        print("Game has ended")
        update_data("schedule", column_updates, game_id)

    # print(row)
    conn.close()
    return game_state
