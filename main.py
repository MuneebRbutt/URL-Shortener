import hashlib
import pyodbc

# Database connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=DESKTOP-TG92T85\MSSQLSERVER01;'  # change if your instance name is different
    'DATABASE=Muneeb;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)
cursor = conn.cursor()

BASE_URL = "http://Butt.url/"



def shorten_url(long_url):
    # Check if URL already exists
    cursor.execute("SELECT short_url FROM UrlShortener WHERE long_url = ?", long_url)
    row = cursor.fetchone()
    if row:
        return BASE_URL + row[0]

    # Create short code
    short_code = hashlib.md5(long_url.encode()).hexdigest()[:6]

    # Ensure no collision
    while True:
        cursor.execute("SELECT id FROM UrlShortener WHERE short_url = ?", short_code)
        if not cursor.fetchone():
            break
        short_code = hashlib.md5((long_url + os.urandom(4).hex()).encode()).hexdigest()[:6]

    # Insert into DB
    cursor.execute(
        "INSERT INTO UrlShortener (long_url, short_url) VALUES (?, ?)",
        (long_url, short_code)
    )
    conn.commit()

    return BASE_URL + short_code


def expand_url(short_code):
    cursor.execute("SELECT long_url FROM UrlShortener WHERE short_url = ?", short_code)
    row = cursor.fetchone()
    return row[0] if row else "No URL found for this code."


def view_history():
    cursor.execute("SELECT long_url, short_url FROM UrlShortener")
    rows = cursor.fetchall()
    if not rows:
        print("No URLs have been shortened yet.")
    else:
        print("\n--- URL Shortening History ---")
        for long_url, short_url in rows:
            print(f"{long_url}  -->  {BASE_URL}{short_url}")
        print("\n")



if __name__ == "__main__":
    import os
    while True:
        choice = input(
            "1: Shorten URL \n2: Expand URL \n3: View History \n4: Exit\nChoose: "
        )

        if choice == "1":
            long_url = input("Enter the long URL: ")
            short = shorten_url(long_url)
            print("Shortened URL:", short)

        elif choice == "2":
            code = input("Enter the short code or full short URL: ").replace(BASE_URL, "")
            original = expand_url(code)
            print("Original URL:", original)

        elif choice == "3":
            view_history()

        elif choice == "4":
            break

        else:
            print("Invalid choice, try again.")

# Close DB connection when done
conn.close()
