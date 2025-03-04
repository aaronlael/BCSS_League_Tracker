
import datetime as dt
import mysql.connector
import os


def connect_to_mysql() -> tuple:
    try:
        mydb = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database")
        )
        return mydb, None
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None, str(err)


def add_player(player_data) -> bool:
    """Adds a player to the BCSS_Players table.

    Args:
        player_data: A dictionary containing player data.
    """
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return False, error_message

    try:
        mycursor = mydb.cursor()
        sql = """
            INSERT INTO BCSS_Players (date, name, tag_in, tag_out, payout_in, CTP1, CTP2, ace_pot, place, payout_dollars)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (
            player_data.get("date"),
            player_data.get("name"),
            player_data.get("tag_in"),
            player_data.get("tag_out"),
            player_data.get("payout_in"),
            player_data.get("CTP1"),
            player_data.get("CTP2"),
            player_data.get("ace_pot"),
            player_data.get("place"),
            player_data.get("payout_dollars")
        )
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
        return True, None #return success and no error
    except mysql.connector.Error as err:
        print(f"Error inserting player: {err}")
        mydb.rollback() #rollback on error
        return False, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()

def get_players(date_str) -> tuple:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor()
        sql = "SELECT id, name FROM BCSS_Players WHERE date = %s"

        # Convert the date string to a datetime.date object for proper comparison
        try:
            date_object = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None, "Invalid date format. Please use YYYY-MM-DD."

        mycursor.execute(sql, (date_object,))  # Use a tuple for parameter binding
        results = mycursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        print(f"Error retrieving players: {err}")
        return None, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()



def update_player_place(player_updates):
    """Updates the 'place' for multiple players in the database.

    Args:
        player_updates: A list of dictionaries, where each dictionary has 'id' and 'place' keys.
    """

    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return False, error_message

    try:
        mycursor = mydb.cursor()
        for player in player_updates:
            player_id = player.get("id")
            player_place = player.get("place")
            player_name = player.get("name")

            if player_id is None or player_place is None:
                print("Error: Player data missing 'id' or 'place'.")
                return False, "Player data missing 'id' or 'place'."

            sql = "UPDATE BCSS_Players SET place = %s, name = %s WHERE id = %s"
            val = (player_place, player_name, player_id)
            mycursor.execute(sql, val)

        mydb.commit()  # Commit changes after all updates
        print(mycursor.rowcount, "record(s) updated.")
        return True, None
    except mysql.connector.Error as err:
        print(f"Error updating player place: {err}")
        mydb.rollback()
        return False, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()


def update_tag_out(date_str):
    mydb, error_message = connect_to_mysql()
    if error_message:
        return False, error_message

    try:
        mycursor = mydb.cursor()

        # 1. Retrieve available tag_in values for the given date
        sql_select_tags = """
            SELECT DISTINCT tag_in
            FROM BCSS_Players
            WHERE date = %s AND tag_in IS NOT NULL
            ORDER BY tag_in ASC
        """
        try:
            date_object = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Please use ентитету-MM-DD."
        mycursor.execute(sql_select_tags, (date_object,))
        available_tags = [tag[0] for tag in mycursor.fetchall()]

        if not available_tags:
            print("No available tags for date")
            return True, None #no error but nothing updated.

        # 2. Retrieve players (id, tag_in) sorted by place and then tag_in
        sql_select_players = """
            SELECT id
            FROM BCSS_Players
            WHERE date = %s AND tag_in IS NOT NULL
            ORDER BY place ASC, tag_in ASC
        """
        mycursor.execute(sql_select_players, (date_object,))
        players = mycursor.fetchall()

        # 3. Assign new tags and update tag_out
        if len(players) > len(available_tags):
            return False, "Not enough unique tag_in values to assign tag_out values"

        for i, (player_id,) in enumerate(players):
            new_tag = available_tags[i]
            sql_update = "UPDATE BCSS_Players SET tag_out = %s WHERE id = %s"
            val_update = (new_tag, player_id)
            mycursor.execute(sql_update, val_update)

        mydb.commit()
        print(mycursor.rowcount, "record(s) updated.")
        return True, None
    except mysql.connector.Error as err:
        print(f"Error updating tag_out: {err}")
        mydb.rollback()
        return False, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()


def get_players_to_pay(current_date):
    mydb, error_message = connect_to_mysql()
    if error_message:
        return False, error_message

    try:
        mycursor = mydb.cursor()
        sql_select_tags = """
            SELECT id, place
            FROM BCSS_Players
            WHERE date = %s AND payout_in > 0
            ORDER BY tag_in ASC
        """
        try:
            date_object = dt.datetime.strptime(current_date, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Please use ентитету-MM-DD."
        mycursor.execute(sql_select_tags, (date_object,))
        return mycursor.fetchall(), None
    except mysql.connector.Error as err:
        print(f"Error retrieving players: {err}")
        return None, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()

def pay_player(player_id: int, payout_value: float) -> tuple[bool, str]:
    mydb, error_message = connect_to_mysql()
    if error_message:
        return False, error_message

    try:
        mycursor = mydb.cursor()
        sql = """
                UPDATE BCSS_Players
                SET payout_dollars = %s
                WHERE id = %s
            """
        val = (payout_value, player_id)
        mycursor.execute(sql, val)
        mydb.commit()  # Important: Commit the changes to the database
        return True, None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False, str(err)
    except Exception as e:
        print(f"An unexpected error occurred: {e}") #catch any other errors
        return False, str(e)
    finally:
        if mycursor:
            mycursor.close()
        if mydb and mydb.is_connected():
            mydb.close()


def wrap_up(current_date):
    mydb, error_message = connect_to_mysql()
    if error_message:
        return False, error_message

    try:
        mycursor = mydb.cursor(dictionary=True) # Important: Use dictionary cursor

        try:
            date_object = dt.datetime.strptime(current_date, "%Y-%m-%d").date()
        except ValueError:
            return None, "Invalid date format. Please use YYYY-MM-DD."

        sql = """
            SELECT name, tag_out, place, payout_dollars
            FROM BCSS_Players
            WHERE date = %s
            ORDER BY place ASC
        """
        mycursor.execute(sql, (date_object,))
        results = mycursor.fetchall()

        return results, None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None, str(err)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, str(e)
    finally:
        if mycursor:
            mycursor.close()
        if mydb and mydb.is_connected():
            mydb.close()


def get_ctp(date_str, ctp: int) -> tuple:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor()
        sql = """SELECT name, id FROM BCSS_CTPS
            WHERE date = %s AND ctp_number = %s
            ORDER BY id DESC"""

        # Convert the date string to a datetime.date object for proper comparison
        try:
            date_object = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None, "Invalid date format. Please use YYYY-MM-DD."

        mycursor.execute(sql, (date_object, ctp))  # Use a tuple for parameter binding
        results = mycursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        print(f"Error retrieving players: {err}")
        return None, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()

def add_ctp(player: str, ctp: int, date_str: str) -> tuple:
    mydb, error_message = connect_to_mysql()
    if error_message:
        return False, error_message

    try:
        mycursor = mydb.cursor()
        sql = """
            INSERT INTO BCSS_CTPS (date, name, ctp_number)
            VALUES (%s, %s, %s)
        """
        val = (
            dt.datetime.strptime(date_str, "%Y-%m-%d").date(),
            player,
            ctp
        )
        mycursor.execute(sql, val)
        mydb.commit()
        return True, None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False, str(err)
    except Exception as e:
        print(f"An unexpected error occurred: {e}") #catch any other errors
        return False, str(e)
    finally:
        if mycursor:
            mycursor.close()
        if mydb and mydb.is_connected():
            mydb.close()


def get_ctp_wrap(date_str) -> tuple:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor()
        sql = """SELECT name, ctp_number, id FROM BCSS_CTPS
            WHERE date = %s
            ORDER BY ctp_number ASC, id ASC"""

        # Convert the date string to a datetime.date object for proper comparison
        try:
            date_object = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None, "Invalid date format. Please use YYYY-MM-DD."

        mycursor.execute(sql, (date_object,))  # Use a tuple for parameter binding
        results = mycursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        print(f"Error retrieving players: {err}")
        return None, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()


def get_tag_holders() -> list:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor()
        sql = """select t1.name, t1.tag_out, t1.date from BCSS_Players t1
        Where t1.date = (select MAX(t2.date) From BCSS_Players t2
            WHERE t2.name = t1.name)
        and t1.tag_out is not null
        ORDER BY tag_out ASC;"""

        mycursor.execute(sql)  # Use a tuple for parameter binding
        results = mycursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        return None, err



def get_tag_history(tag) -> list:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor()
        sql = """select name, tag_out, date from BCSS_Players
        WHERE tag_out = %s
        ORDER BY date DESC"""

        mycursor.execute(sql, (tag,))  # Use a tuple for parameter binding
        results = mycursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        return None, err


def get_player_history(player) -> list:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor()
        sql = """select name, tag_out, date from BCSS_Players
        WHERE name = %s
        ORDER BY date DESC"""

        mycursor.execute(sql, (player,))  # Use a tuple for parameter binding
        results = mycursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        return None, err

def get_players_detailed(date_str) -> tuple:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor(dictionary=True)
        sql = "SELECT id, name, tag_in, payout_in, CTP1, CTP2, ace_pot FROM BCSS_Players WHERE date = %s"

        # Convert the date string to a datetime.date object for proper comparison
        try:
            date_object = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None, "Invalid date format. Please use YYYY-MM-DD."

        mycursor.execute(sql, (date_object,))  # Use a tuple for parameter binding
        results = mycursor.fetchall()
        return results, None
    except mysql.connector.Error as err:
        print(f"Error retrieving players: {err}")
        return None, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()

def delete_player(id: int) -> None:
    mydb, error_message = connect_to_mysql()
    if error_message:
        print(f"Database connection issue: {error_message}")
        return None, error_message

    try:
        mycursor = mydb.cursor()
        sql = "DELETE FROM BCSS_Players WHERE id = %s"
        mycursor.execute(sql, (id,))
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error retrieving players: {err}")
        return None, str(err)
    finally:
        if mydb and mydb.is_connected():
            mycursor.close()
            mydb.close()
