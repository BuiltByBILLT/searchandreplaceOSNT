import mysql.connector
import json

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  # Local by Flywheel usually uses 'localhost'
        port=10011,  # Confirm the port number is correct
        user='root',  # The default user for Local by Flywheel
        password='root',  # The default password for Local by Flywheel
        database='local'  # Replace with your actual database name from Local by Flywheel
    )

def get_site_url(cursor):
    cursor.execute("SELECT option_value FROM wp_options WHERE option_name = 'siteurl'")
    result = cursor.fetchone()
    return result[0] if result else ''

def search_string_in_pages(search_term):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT ID, post_title, post_content, post_name FROM wp_posts WHERE post_type = 'page' AND post_content LIKE %s", ('%' + search_term + '%',))
    results = cursor.fetchall()

    phrases = {
        "Dr. Greg Rohn and ": [],
        "Dr. Rohn and ": [],
        "Dr Rohn and ": [],
        "Dr. Greg Rohn, ": [],
        "Dr. Rohn, ": [],
        "Dr Rohn, ": [],
        "Other": [],
        "Multiple": [],
        "Review": []
    }
    needs_review = [113, 138, 845, 109, 1704, 109, 559, 1551, 1648, 105, 586, 665, 46, 52, 78, 103, 3010]

    total_count = 0
    site_url = "https://entkidsadults.com"


    for page in results:
        post_id, post_title, post_content, post_name = page
        lines = post_content.split('\n')
        url = f"{site_url}/{post_name}"
        for line in lines:
            if search_term in line:
                count = line.count(search_term)
                total_count += count
                
                # send to review
                if post_id in needs_review:
                    phrases["Review"].append({
                        "post_id": post_id,
                        "post_title": post_title,
                        "url": url,
                        "line": line,
                        "cleaned": line
                    })
                    continue

                # multiple instances of search term
                if count > 1:
                    phrases["Multiple"].append({
                        "post_id": post_id,
                        "post_title": post_title,
                        "url": url,
                        "line": line,
                        "cleaned": line
                    })
                    continue

                # check for specific phrases
                phraseMatch = False
                for phrase in phrases.keys():
                    if phrase in line:
                        cleaned = line.replace(phrase, "")
                        phrases[phrase].append({
                            "post_id": post_id,
                            "post_title": post_title,
                            "url": url,
                            "line": line,
                            "cleaned": cleaned
                        })
                        phraseMatch = True
                        break
                if not phraseMatch:
                    phrases["Other"].append({
                        "post_id": post_id,
                        "post_title": post_title,
                        "url": url,
                        "line": line,
                        "cleaned": line
                    })

    with open('search-output.json', 'w', encoding='utf-8') as file:
        json.dump(phrases, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    search_term = "Rohn"
    search_string_in_pages(search_term)
