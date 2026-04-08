import sqlite3
import pandas as pd # Optional: if you have pandas installed

def check_my_data():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    
    print("\n--- CURRENT DATABASE STATE ---")
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    
    # Column Headers for clarity
    print(f"{'ID':<15} | {'Status':<15} | {'Address':<30} | {'Price':<10} | {'HITL Lock'}")
    print("-" * 85)
    
    for row in rows:
        print(f"{row[0]:<15} | {row[1]:<15} | {row[2]:<30} | {row[3]:<10} | {row[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_my_data()