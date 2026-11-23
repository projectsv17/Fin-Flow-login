
from database.db_connection import get_connection

try:
    connection = get_connection()

    if connection.is_connected():
        print("SUCCESS!")
        print("MySQL Database Connected!")
        print("Database: fin_flow_ai")

    connection.close()

except Exception as error:
    print("DATABASE CONNECTION FAILED!")
    print(error)
