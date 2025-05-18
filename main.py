import load
import time
import os
import datetime
import sqlite3
from dotenv import load_dotenv

load_dotenv()


# check to see if there is a game running. If so, retrieve the box score on a loop until the game is over
def run():
    current_time_utc = time.time()

    # date_string = "2025-05-11T23:30:00Z"
    # datetime_object = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    # timestamp = time.mktime(datetime_object.timetuple())
    # print(timestamp)

    # search for scheduled games that are running
    try:
        conn = sqlite3.connect(load.DB_FILE)
        conn.row_factory = sqlite3.Row  # Enable access by column name
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM schedule WHERE gameState=1 ORDER BY startTimeUTC ASC")
        row = cursor.fetchone()

        if row:
            result = dict(row)  # Convert sqlite3.Row to a dictionary
        else:
            return None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    game_id = result["id"]
    if int(game_id) > 0:
        run_score_clock(game_id)

    conn.close()
    return None


# Poll NHL box score api in a loop until the game is over
def run_score_clock(game_id):
    game_is_running = 1
    while game_is_running == 1:
        game_is_running = load.load_box_score(game_id)
        time.sleep(int(os.getenv('POLL_FREQUENCY_IN_SECS')))


# Still need to loop once a minute through the schedule and update the game state of all games
while True:
    load.load_team_scoreboard()
    run()
    time.sleep(60)
