import mysql.connector
import json
import logging

# Configure logging
logging.basicConfig(filename='update_db.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Local by Flywheel usually uses 'localhost'
            port=10011,  # Confirm the port number is correct
            user='root',  # The default user for Local by Flywheel
            password='root',  # The default password for Local by Flywheel
            database='local'  # Replace with your actual database name from Local by Flywheel
        )
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database: {err}")
        raise

def update_db_with_cleaned_lines():
    try:
        # Load the JSON file
        with open('search-output-edited.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        logging.error(f"Error loading JSON file: {e}")
        return
    
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Iterate over the phrases and their instances
        for phrase, instances in data.items():
            for instance in instances:
                post_id = instance["post_id"]
                line = instance["line"]
                cleaned_line = instance["cleaned"]
                
                try:
                    # Fetch the current post_content from the database
                    cursor.execute("SELECT post_content FROM wp_posts WHERE ID = %s", (post_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        post_content = result[0]
                        if line in post_content:
                            updated_content = post_content.replace(line, cleaned_line)
                            
                            # Update the post_content in the database
                            cursor.execute("UPDATE wp_posts SET post_content = %s WHERE ID = %s", (updated_content, post_id))
                            connection.commit()
                            logging.info(f"Post ID {post_id} updated successfully.")
                        else:
                            logging.warning(f"Line not found in post_content for Post ID {post_id}. Skipping update.")
                    else:
                        logging.warning(f"No post found with ID {post_id}. Skipping update.")
                
                except mysql.connector.Error as err:
                    logging.error(f"Error updating Post ID {post_id}: {err}")
        
        cursor.close()
        connection.close()
    
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    update_db_with_cleaned_lines()
