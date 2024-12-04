import sqlite3

# Connect to the Chinook database
db_file = "assets/Chinook.db"
db_conn = sqlite3.connect(db_file)

# Create a cursor object
cursor = db_conn.cursor()

# Define the SQL query
sql_query = """
SELECT T1.Title FROM Album AS T1 JOIN Artist AS T2 ON T1.ArtistId  =  T2.ArtistId WHERE T2.Name  =  'AC/DC'
"""

# Execute the query
cursor.execute(sql_query)

# Fetch all results
results = cursor.fetchall()

# Print the results
for row in results:
    print(row)

# Close the connection
db_conn.close()