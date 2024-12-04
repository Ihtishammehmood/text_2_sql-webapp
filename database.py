import pandas as pd
import sqlite3

# Define file paths
csv_file = "assets\Car_prices.csv"
db_file = "assets\car_price.db"

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file)

# Connect to (or create) the SQLite database
conn = sqlite3.connect(db_file)

# Write the DataFrame to a new table in the SQLite database
# The table name is 'car_prices'
df.to_sql('car_prices', conn, if_exists='replace', index=False)

# Close the database connection
conn.close()

print("CSV data has been successfully converted to SQLite database.")