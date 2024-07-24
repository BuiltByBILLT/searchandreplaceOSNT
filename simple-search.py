import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  
        port=10011,  
        user='root',  
        password='root',  
        database='local'  
    )

def search_string_in_pages(search_term):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT ID, post_title, post_content FROM wp_posts WHERE post_type = 'page' AND post_content LIKE %s", ('%' + search_term + '%',))
    results = cursor.fetchall()

    with open('simple-search-output.txt', 'w', encoding='utf-8') as file:
        for page in results:
            post_id, post_title, post_content = page
            lines = post_content.split('\n')
            for line in lines:
                if search_term in line:
                    file.write(f"Page ID: {post_id}, Title: {post_title}\n")
                    file.write(f"Line: {line.strip()}\n\n")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    search_term = "Rohn"
    search_string_in_pages(search_term)
