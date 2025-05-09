import database.db_config as db_config

def get_app_config():
    """
    Fetches all app configuration parameters from the database.
    
    Returns:
        dict: Dictionary with config keys and their values
    """
    config_data = {}
    conn = None
    try:
        # Connect to the database
        conn = db_config.connect_to_database()
        cursor = conn.cursor()
        
        # Execute query to get all config entries
        cursor.execute("SELECT key, value FROM app_config")
        
        # Convert results to dictionary
        for row in cursor.fetchall():
            key, value = row
            config_data[key] = value
            
    except Exception as e:
        print(f"Error fetching app config: {e}")
    finally:
        # Close the connection
        if conn:
            db_config.close_database_connection(conn)
            
    return config_data

def get_app_config_value(key, default=None):
    """
    Get a specific configuration value from the app_config table.
    
    Args:
        key (str): The configuration key to look up
        default: Value to return if the key is not found
        
    Returns:
        The value for the specified key or the default if not found
    """
    conn = None
    try:
        # Connect to the database
        conn = db_config.connect_to_database()
        cursor = conn.cursor()
        
        # Execute query to get the specific config entry
        cursor.execute("SELECT value FROM app_config WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        return default
            
    except Exception as e:
        print(f"Error fetching app config value for key '{key}': {e}")
        return default
    finally:
        # Close the connection
        if conn:
            db_config.close_database_connection(conn)