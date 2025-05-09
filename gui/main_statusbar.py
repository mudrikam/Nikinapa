from PyQt6.QtWidgets import QStatusBar
from PyQt6.QtGui import QPalette, QColor


class MainStatusBar(QStatusBar):
    """
    Main status bar for the application.
    Provides status updates to the user.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components of the status bar."""
        # Status bar is initially empty
        self.showMessage("Ready", 2000)
        # Set the style of the status bar 
        self.setStyleSheet("QStatusBar { color: rgba(127, 127, 127, 0.1); }")