import sys
from pathlib import Path

# Add the root directory to the Python path to make imports work correctly
root_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(root_dir))

# Now import the database module
from database.db_config import main as create_database
from gui.main_window import create_main_window

# Create the database file if it doesn't exist
db_path = create_database(str(root_dir))

# Create and run the main application window
if __name__ == "__main__":
    # Create the main window
    app, window = create_main_window()
    
    # Start the application event loop
    sys.exit(app.exec())
