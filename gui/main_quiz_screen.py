from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QFrame, QSizePolicy, QHBoxLayout
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtCore import Qt, QSize


class MainQuizScreen(QWidget):
    """
    Simple widget that mimics a Who Wants to Be a Millionaire question screen.
    Shows a question at the top and 4 option buttons below.
    Uses system colors for consistency.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get system palette colors for theming
        self.palette = self.palette()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup all UI components of the quiz screen widget"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top frame - add background for debugging
        top_frame = QFrame()
        top_frame.setFrameShape(QFrame.Shape.NoFrame)
        top_frame_layout = QHBoxLayout(top_frame)  # Use horizontal layout to arrange sections
        
        # Create three frames for the sections
        left_frame = QFrame()
        middle_frame_stats = QFrame()  # Renamed to avoid conflict with question middle_frame
        right_frame = QFrame()
        
        # Set up layouts for each section
        left_layout = QVBoxLayout(left_frame)
        middle_layout = QVBoxLayout(middle_frame_stats)
        right_layout = QVBoxLayout(right_frame)
        
        # Left section - Score, Correct, Incorrect
        score_label = QLabel("Score: 0")
        score_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        correct_label = QLabel("Correct: 0")
        correct_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        incorrect_label = QLabel("Incorrect: 0")
        incorrect_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        
        left_layout.addWidget(score_label)
        left_layout.addWidget(correct_label)
        left_layout.addWidget(incorrect_label)
        left_layout.addStretch()  # Add stretch to align widgets to the top
        
        # Store references for later updates
        self.score_label = score_label
        self.correct_label = correct_label
        self.incorrect_label = incorrect_label
        
        # Middle section - Time statistics
        fastest_label = QLabel("Fastest: 0:00")
        fastest_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        slowest_label = QLabel("Slowest: 0:00")
        slowest_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        average_label = QLabel("Average: 0:00")
        average_label.setStyleSheet("font-size: 12pt; font-weight: 600;")
        
        middle_layout.addWidget(fastest_label)
        middle_layout.addWidget(slowest_label)
        middle_layout.addWidget(average_label)
        middle_layout.addStretch()  # Add stretch to align widgets to the top
        
        # Store references for later updates
        self.fastest_label = fastest_label
        self.slowest_label = slowest_label
        self.average_label = average_label
        
        # Right section - Lock Answer button and Clear Answer button
        lock_button = QPushButton("Lock Answer")
        # Initial state - disabled until an answer is selected
        lock_button.setEnabled(False)
        
        # Create Clear Answer button
        clear_button = QPushButton("Clear Answer")
        clear_button.clicked.connect(self.clear_answer)
        # Initial state - disabled until an answer is selected (same as lock button)
        clear_button.setEnabled(False)
        
        # Apply consistent styling to both buttons
        for btn in [lock_button, clear_button]:
            font = QFont()
            font.setPointSize(12)
            btn.setFont(font)
            btn.setMinimumHeight(40)
            btn.setContentsMargins(10, 10, 10, 10)
            btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            
        # No stylesheet initially - we'll set it in handle_button_selection
        
        # Connect Lock Answer button click
        lock_button.clicked.connect(self.lock_answer)
        
        # Add stretch, buttons, and stretch to center them vertically
        right_layout.addStretch(1)
        right_layout.addWidget(lock_button)
        right_layout.addWidget(clear_button)
        right_layout.addStretch(1)
        
        # Store reference for later use
        self.lock_button = lock_button
        self.clear_button = clear_button
        
        # Add frames to the top layout with stretch factors
        top_frame_layout.addWidget(left_frame, 1)
        top_frame_layout.addWidget(middle_frame_stats, 1)
        top_frame_layout.addWidget(right_frame, 1)
        
        # Middle frame - add second frame below question section
        middle_frame = QFrame()
        middle_frame.setFrameShape(QFrame.Shape.NoFrame)
        middle_frame_layout = QVBoxLayout(middle_frame)
        
        # Add large question text to middle frame with stylesheet
        question_label = QLabel("This is question section")
        question_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: 600;
            qproperty-alignment: AlignCenter;
        """)
        middle_frame_layout.addWidget(question_label)
        
        # Bottom frame - add background for debugging
        bottom_frame = QFrame()
        bottom_frame.setFrameShape(QFrame.Shape.NoFrame)
        
        # Add grid layout for buttons
        bottom_frame_layout = QGridLayout(bottom_frame)
        bottom_frame_layout.setSpacing(10)
        
        # Create 4 buttons in a 2-column grid
        button_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]  # Row, Column
        button_prefixes = ["A. ", "B. ", "C. ", "D. "]
        self.answer_buttons = []  # Store buttons for selection control
        
        for i, (pos, prefix) in enumerate(zip(button_positions, button_prefixes), 1):
            # Create button with regular text (no HTML)
            button = QPushButton(f"{prefix}Button {i}")
            button.setMinimumHeight(60)
            button.setCheckable(True)
            
            # Connect button click to selection handler
            button.clicked.connect(lambda checked, btn=button: self.handle_button_selection(btn))
            
            button.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 8px 8px 20px;
                    background-color: transparent;
                    border: 2px solid palette(mid);
                    border-style: solid;
                    border-radius: 30px;
                    font-size: 12pt;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #FFA500;  /* Yellow-orange color */
                    color: black;
                }
                QPushButton:checked {
                    background-color: #FFA500;  /* Same yellow-orange for selected state */
                    color: black;
                }
            """)
            
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            bottom_frame_layout.addWidget(button, pos[0], pos[1])
            self.answer_buttons.append(button)
        
        # Add frames to main layout
        main_layout.addWidget(top_frame, 1)
        main_layout.addWidget(middle_frame, 2)
        main_layout.addWidget(bottom_frame, 1)
    
    def handle_button_selection(self, clicked_button):
        """Ensure only one button is selected at a time and update lock button appearance"""
        # First uncheck all other buttons
        for button in self.answer_buttons:
            if button != clicked_button:
                button.setChecked(False)
        
        # Change button color to green if any answer is selected
        is_any_selected = any(button.isChecked() for button in self.answer_buttons)
        if is_any_selected:
            # Use !hover selector to make sure our hover state is properly applied
            self.lock_button.setStyleSheet("""
                QPushButton {
                    font-size: 12pt;
                    padding: 10px;
                    background-color: #008000;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #006400 !important;
                    color: white;
                }
            """)
            self.lock_button.setEnabled(True)
            # Also enable the clear button when an answer is selected
            self.clear_button.setEnabled(True)
        else:
            # Reset to default style if no button is selected
            self.lock_button.setStyleSheet("""
                QPushButton {
                    font-size: 12pt;
                    padding: 10px;
                }
            """)
            self.lock_button.setEnabled(False)
            # Also disable the clear button when no answer is selected
            self.clear_button.setEnabled(False)
    
    def lock_answer(self):
        """Handle the lock answer button click"""
        print("Answer locked!")
    
    def clear_answer(self):
        """Handle the clear answer button click"""
        # Uncheck all answer buttons
        for button in self.answer_buttons:
            button.setChecked(False)
        
        # Update button states to reflect no selection
        self.handle_button_selection(None)