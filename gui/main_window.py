from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QVBoxLayout
from PyQt6.QtGui import QIcon
import sys
import os
from database.db_app_window import get_app_config
import database.db_config as db_config
from gui.main_statusbar import MainStatusBar
from gui.main_quiz_screen import MainQuizScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load configuration from database - required for application to function
        self.app_config = get_app_config()
        
        # Check if we got the required configuration data
        if not self.app_config:
            self.show_error_and_exit("Couldn't load configuration from database")
            return
            
        self.setup_window()
        self.setup_statusbar()
        self.setup_central_widget()
        
    def show_error_and_exit(self, message):
        """Show error message and exit application."""
        QMessageBox.critical(None, "Database Error", message)
        sys.exit(1)
        
    def setup_window(self):
        """Configure the main window settings."""
        # Set window title from database config with app name and version
        if 'app_name' not in self.app_config or 'app_version' not in self.app_config:
            self.show_error_and_exit("Missing 'app_name' or 'app_version' in database configuration")
            return
            
        app_name = self.app_config['app_name']
        app_version = self.app_config['app_version']
        self.setWindowTitle(f"{app_name} v{app_version}")
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "resources", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Set window size from database config
        if 'window_width' not in self.app_config or 'window_height' not in self.app_config:
            self.show_error_and_exit("Missing window dimensions in database configuration")
            return
            
        try:
            window_width = int(self.app_config['window_width'])
            window_height = int(self.app_config['window_height'])
        except (ValueError, TypeError):
            self.show_error_and_exit("Invalid window dimensions in database configuration")
            return
        
        # Get the screen geometry
        screen = self.screen().geometry()
        
        # Calculate position for center of screen
        x_position = (screen.width() - window_width) // 2
        y_position = (screen.height() - window_height) // 2
        
        # Set window size and position
        self.setGeometry(x_position, y_position, window_width, window_height)
        
    def setup_statusbar(self):
        """Setup the status bar for the main window."""
        self.statusbar = MainStatusBar(self)
        self.setStatusBar(self.statusbar)
        
    def setup_central_widget(self):
        """Setup the central widget with the quiz screen widget."""
        # Create the quiz screen widget directly as the central widget
        self.quiz_widget = MainQuizScreen(self)
        self.setCentralWidget(self.quiz_widget)


def create_main_window():
    """Create and return the main application window."""
    app = QApplication(sys.argv)
    
    # Initialize database configuration
    db_path = db_config.main()
    
    if not os.path.exists(db_path):
        QMessageBox.critical(None, "Database Error", f"Database file not found at {db_path}")
        sys.exit(1)
    
    # Set application icon for the entire application
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           "resources", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    return app, window