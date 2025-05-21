import sys
import json
import random
import time
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QHBoxLayout, QLabel, QSizePolicy, QProgressBar
from PySide6.QtCore import QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

# Import Google's Generative AI library
# To install: pip install google-genai
from google import genai
from google.genai import types

# Configure the Gemini API
API_KEY = "AIzaSyDmTk0dta-zMBVFpsLgPH2vfNOpw4fsNTs"
# Initialize the Gemini client with the API key
client = genai.Client(api_key=API_KEY)

class QuizGame:
    def __init__(self):
        # Load the UI
        loader = QUiLoader()
        self.ui = loader.load("quiz.ui")
        self.ui.setWindowTitle("Brainstorm Bakery v1.0.0")
        
        # Ensure fixed size
        self.ui.setFixedSize(800, 600)
        
        # Set the application icon
        icon = QIcon("cake.ico")
        self.ui.setWindowIcon(icon)
        
        # Get reference to the progress bar from UI
        self.progress_bar = self.ui.progress_bar
        
        # Create a timer for the countdown
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_remaining = 0
        
        # Create a timer for delayed transition
        self.delay_timer = QTimer()
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self.next_question)
        
        # Hide trivia label initially
        self.ui.lbl_trivia.setVisible(False)
        
        # Answer buttons
        self.buttons = {
            'A': self.ui.btn_A,
            'B': self.ui.btn_B,
            'C': self.ui.btn_C,
            'D': self.ui.btn_D
        }
        
        # Current question data
        self.current_question = None
        self.correct_answer = None
        
        # Initialize score counters
        self.correct_count = 0
        self.incorrect_count = 0
        
        # Load the highest score from the JSON file
        self.highest_score = self.load_highest_score()
        self.update_highest_score_display()
        
        # Initialize timer state
        self.timer_paused = False
        
        # Connect buttons to their handlers with explicit button identification
        self.ui.btn_A.clicked.connect(lambda: self.check_answer('A'))
        self.ui.btn_B.clicked.connect(lambda: self.check_answer('B'))
        self.ui.btn_C.clicked.connect(lambda: self.check_answer('C'))
        self.ui.btn_D.clicked.connect(lambda: self.check_answer('D'))
        
        self.ui.btn_next.clicked.connect(self.next_question)
        
        # Connect the pause button
        self.ui.btn_pause.clicked.connect(self.toggle_pause)
        
        # Initialize stopwatch
        self.stopwatch_timer = QTimer()
        self.stopwatch_timer.timeout.connect(self.update_stopwatch)
        self.stopwatch_start_time = 0
        self.stopwatch_elapsed = 0
        
        # Set up timer for baking time
        self.start_time = time.time()
        self.baking_timer = QTimer()
        self.baking_timer.timeout.connect(self.update_baking_time)
        self.baking_timer.start(1000)  # Update every second
        
        # Load categories from JSON file
        self.categories = self.load_categories()
        
        # Get the first question when starting
        self.next_question()
        
        # Show the UI
        self.ui.show()
        
    def load_categories(self):
        """Load categories from JSON file"""
        try:
            # Check if the categories file exists
            categories_file = "quiz_categories.json"
            if os.path.exists(categories_file):
                with open(categories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("categories", [])
            else:
                print("Categories file not found. Using default categories.")
                # Return a small default set if file not found
                return ["Pengetahuan Umum", "Sains", "Sejarah", "Geografi", "Hiburan"]
        except Exception as e:
            print(f"Error loading categories: {e}")
            # Return a small default set in case of error
            return ["Pengetahuan Umum", "Sains", "Sejarah", "Geografi", "Hiburan"]
        
    def load_highest_score(self):
        """Load the highest score from the JSON file"""
        try:
            # Check if the score file exists
            score_file = "quiz_score.json"
            if os.path.exists(score_file):
                with open(score_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load the longest baking time as well
                    longest_time = data.get("longest_baking_time", 0)
                    self.longest_baking_time = longest_time
                    print(f"Loaded highest score: {data.get('highest_score', 0)} with baking time: {self.format_time(longest_time)}")
                    return data.get("highest_score", 0)
            else:
                print("Score file not found. Creating a new one.")
                # Create the file if it doesn't exist
                self.longest_baking_time = 0
                data = {"highest_score": 0, "longest_baking_time": 0}
                with open(score_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                return 0
        except Exception as e:
            print(f"Error loading highest score: {e}")
            self.longest_baking_time = 0
            return 0

    def save_highest_score(self, score):
        """Save the highest score to the JSON file"""
        try:
            score_file = "quiz_score.json"
            
            # Get the current baking time directly from the UI label
            current_time_str = self.ui.lbl_baking_time.text()
            # Convert HH:MM:SS format to seconds
            h, m, s = current_time_str.split(':')
            current_baking_time = int(h) * 3600 + int(m) * 60 + int(s)
            
            # Debug output to check the values
            print(f"Current baking time from UI: {current_time_str} ({current_baking_time} seconds)")
            
            # Prepare data to save
            data = {}
            
            # Try to load existing data first to preserve structure
            if os.path.exists(score_file):
                try:
                    with open(score_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"Loaded existing data: {data}")
                except Exception as e:
                    print(f"Error reading existing score file: {e}")
                    # If file exists but can't be read, start fresh
                    pass
            
            # Only update the highest score and baking time if this is a new high score
            if score > data.get("highest_score", 0):
                data["highest_score"] = score
                data["longest_baking_time"] = current_baking_time
                self.longest_baking_time = current_baking_time
                print(f"New highest score: {score} with baking time: {current_time_str}")
            elif score == data.get("highest_score", 0) and "highest_score" in data:
                # If equal score but longer time, don't update
                print(f"Equal score {score}, keeping existing time: {self.format_time(data.get('longest_baking_time', 0))}")
            else:
                # This is a lower score, keep existing high score and time
                print(f"Lower score {score} vs existing {data.get('highest_score', 0)}, no update needed")
                return
            
            # Save the updated data
            with open(score_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                print(f"Saved data: {data}")
                print(f"Highest score {data['highest_score']} saved with baking time: {self.format_time(data['longest_baking_time'])}")
        except Exception as e:
            print(f"Error saving highest score: {e}")
            import traceback
            traceback.print_exc()
    
    def format_time(self, seconds):
        """Format seconds into hours:minutes:seconds"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def update_highest_score(self):
        """Update the highest score if the current score is higher"""
        if self.correct_count > self.highest_score:
            self.highest_score = self.correct_count
            self.save_highest_score(self.highest_score)
        self.update_highest_score_display()
    
    def update_highest_score_display(self):
        """Update the highest score display in the UI"""
        if self.highest_score > 0:
            formatted_time = self.format_time(self.longest_baking_time)
            self.ui.lbl_highest_count.setText(f"{self.highest_score}, after roasting the brain for {formatted_time}")
        else:
            self.ui.lbl_highest_count.setText("No brain had been baked")
        
    def toggle_pause(self):
        """Toggle the pause state for the delay timer"""
        if self.timer_paused:
            # Resume timer
            self.delay_timer.start(self.remaining_delay_time)
            self.ui.btn_pause.setText("Pause")
            self.timer_paused = False
        else:
            # Pause timer
            self.remaining_delay_time = self.delay_timer.remainingTime()
            self.delay_timer.stop()
            self.ui.btn_pause.setText("Resume")
            self.timer_paused = True
        
    def generate_question(self):
        """Generate a question using Gemini API"""
        # Show "Tunggu sebentar..." message initially
        self.ui.lbl_question.setText("Tunggu sebentar...")
        QApplication.processEvents()  # Force UI update

        max_retries = 3
        retry_count = 0
        retry_delay = 2  # seconds

        while retry_count < max_retries:
            try:
                # Get current timestamp to help generate unique questions
                timestamp = int(time.time())
                
                # Select a random category from loaded categories
                category = random.choice(self.categories)
                
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(
                        system_instruction="You are a fun trivia question generator. You generate only valid JSON with a trivia question having one question, 4 multiple-choice options labeled A, B, C, D, and one correct answer letter, and a short trivia explanation about the correct answer. IMPORTANT: Create engaging questions in Indonesian language suitable for students of all levels. AVOID programming, technical computer science questions, and overly specialized topics. Ensure variety by rotating through different categories with each question - never stick to the same topic for consecutive questions. Mix fun facts, academic knowledge, pop culture, science, history, arts, sports, and general knowledge. Questions should be interesting, educational, and brain-refreshing. Always include a brief, interesting trivia fact about the correct answer."
                    ),
                    contents=f"""Create a fun, unique trivia question in Indonesian language with 4 choices where only one is correct. Make it suitable for students of all ages.

Use this category for the current question: {category}

The question should be fun, educational, and refreshing - avoid being too nationalistic or repetitive. Don't overuse "Indonesia" in the question.

Current timestamp: {timestamp}.
Avoid making the question reapeated or similar to previous timestamp.
                    
Return ONLY a JSON with this structure:
{{
    "question": "Pertanyaan menarik?",
    "options": {{
        "A": "Pilihan pertama",
        "B": "Pilihan kedua",
        "C": "Pilihan ketiga",
        "D": "Pilihan keempat"
    }},
    "correct": "A",
    "trivia": "Fakta menarik tentang jawaban yang benar."
}}
"""
                )
                
                response_text = response.text
                
                # Extract the JSON part from the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_part = response_text[json_start:json_end]
                    try:
                        question_data = json.loads(json_part)
                        # Validate the response format
                        if all(key in question_data for key in ["question", "options", "correct", "trivia"]):
                            return question_data
                        else:
                            if "trivia" not in question_data:
                                # If trivia is missing but other fields are valid, add a default trivia
                                if all(key in question_data for key in ["question", "options", "correct"]):
                                    question_data["trivia"] = "Fakta menarik tidak tersedia untuk jawaban ini."
                                    return question_data
                            
                            print(f"Missing required keys in response: {question_data.keys()}")
                            retry_count += 1
                            if retry_count >= max_retries:
                                raise Exception(f"Invalid question format after {max_retries} attempts: missing keys. Got {list(question_data.keys())}")
                            print(f"Retrying ({retry_count}/{max_retries})...")
                            time.sleep(retry_delay)
                            continue
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON from API response: {e}")
                        retry_count += 1
                        if retry_count >= max_retries:
                            raise Exception(f"Invalid JSON from Gemini after {max_retries} attempts: {e}")
                        print(f"Retrying ({retry_count}/{max_retries})...")
                        time.sleep(retry_delay)
                        continue
                else:
                    print("Could not find JSON in the response")
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"Could not extract JSON from Gemini response after {max_retries} attempts")
                    print(f"Retrying ({retry_count}/{max_retries})...")
                    time.sleep(retry_delay)
                    continue
                
            except Exception as e:
                if "429" in str(e) or "503" in str(e) or "unavailable" in str(e).lower():
                    # Handle rate limiting or service unavailability with retries
                    retry_count += 1
                    wait_time = retry_delay * retry_count  # Exponential backoff
                    print(f"Gemini API temporarily unavailable: {e}. Waiting {wait_time}s before retry ({retry_count}/{max_retries})...")
                    self.ui.lbl_question.setText(f"Tunggu sebentar... ({retry_count}/{max_retries})")
                    QApplication.processEvents()  # Force UI update
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Error generating question: {e}")
                    self.show_error(f"Error getting question from Gemini: {str(e)}")
                    sys.exit(1)  # Exit the application if no question can be generated
        
        # If we've exhausted all retries
        self.show_error(f"Failed to generate a valid question after {max_retries} attempts")
        sys.exit(1)
            
    def show_error(self, message):
        """Show an error message and exit"""
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setText("Error")
        error_box.setInformativeText(message)
        error_box.setWindowTitle("Quiz Error")
        error_box.exec()
    
    def update_timer(self):
        """Update the progress bar timer"""
        self.time_remaining -= 0.1  # Decrease by 0.1 seconds
        
        # Calculate percentage remaining
        percentage = (self.time_remaining / 10.0) * 100  # Changed from 5.0 to 10.0 seconds
        self.progress_bar.setValue(int(percentage))
        
        # If time runs out
        if self.time_remaining <= 0:
            self.timer.stop()
            self.time_out()
    
    def update_stopwatch(self):
        """Update the stopwatch display"""
        elapsed = (time.time() - self.stopwatch_start_time) * 1000  # milliseconds
        self.stopwatch_elapsed = elapsed  # Store for when answer is selected
        self.ui.lbl_stopwatch.setText(f"{elapsed/1000:.3f}s")
    
    def update_baking_time(self):
        """Update the baking time display"""
        elapsed_seconds = int(time.time() - self.start_time)
        hours = elapsed_seconds // 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.ui.lbl_baking_time.setText(time_str)
    
    def time_out(self):
        """Handle when time runs out for a question"""
        # Stop the stopwatch
        self.stopwatch_timer.stop()
        self.ui.lbl_response_time.setText("Time out!")
        
        # Disable all buttons
        for btn in self.buttons.values():
            btn.setEnabled(False)
        
        # Highlight the correct answer in green
        self.buttons[self.correct_answer].setStyleSheet("background-color: #5cb85c; color: white; font-weight: bold; border: 2px solid #4cae4c; border-radius: 5px;")
        
        # Increment incorrect count
        self.incorrect_count += 1
        self.ui.lbl_incorrect_count.setText(str(self.incorrect_count))
        
        # Show trivia about the correct answer
        if hasattr(self, 'current_trivia') and self.current_trivia:
            self.ui.lbl_trivia.setText(self.current_trivia)
            self.ui.lbl_trivia.setVisible(True)
            
            # Show pause button when trivia is displayed
            self.ui.btn_pause.setVisible(True)
        
        # Start the delay timer for automatic progression
        self.remaining_delay_time = 10000  # 10 seconds delay
        self.delay_timer.start(self.remaining_delay_time)
    
    def next_question(self):
        """Load the next question"""
        # Stop any active timers
        self.timer.stop()
        self.delay_timer.stop()
        
        # Hide the trivia label and pause button when showing a new question
        self.ui.lbl_trivia.setVisible(False)
        self.ui.btn_pause.setVisible(False)
        
        # Reset button styling
        for btn in self.buttons.values():
            btn.setStyleSheet("")
            btn.setEnabled(True)
        
        # Reset pause state
        self.timer_paused = False
        self.ui.btn_pause.setText("Pause")
        
        # Reset the stopwatch and make it visible
        self.ui.lbl_stopwatch_text.setVisible(True)
        self.ui.lbl_stopwatch.setVisible(True)
        self.ui.lbl_response_time.setText("")
        self.stopwatch_start_time = time.time()
        self.stopwatch_timer.start(10)  # Update every 10ms for smooth display
        
        # Get a new question
        question_data = self.generate_question()
        
        # Update the UI with the new question
        self.ui.lbl_question.setText(question_data["question"])
        
        # Set the button texts
        for option, text in question_data["options"].items():
            self.buttons[option].setText(f"{option}: {text}")
        
        # Store the correct answer
        self.correct_answer = question_data["correct"]
        
        # Store trivia information
        self.current_trivia = question_data.get("trivia", "")
        
        # Enable the next button only after an answer is chosen
        self.ui.btn_next.setEnabled(False)
        
        # Reset and start the timer
        self.time_remaining = 10.0  # Changed from 5.0 to 10.0 seconds
        self.progress_bar.setValue(100)
        self.timer.start(100)  # Update every 0.1 seconds
    
    def check_answer(self, option=None):
        """Check if the chosen answer is correct"""
        # Stop the timer and stopwatch when an answer is selected
        self.timer.stop()
        self.stopwatch_timer.stop()
        
        # Calculate response time
        response_time = self.stopwatch_elapsed
        response_time_text = f"Response time: {response_time/1000:.3f}s"
        self.ui.lbl_response_time.setText(response_time_text)
        
        chosen_answer = option
        sender_button = None
        
        # If called without an option parameter, try to determine from sender
        if chosen_answer is None:
            sender_button = self.ui.sender()
            for opt, button in self.buttons.items():
                if button == sender_button:
                    chosen_answer = opt
                    break
        else:
            # We already know which button from the lambda
            sender_button = self.buttons[chosen_answer]
        
        if chosen_answer is None:
            print("Error: Could not determine which button was clicked")
            return
        
        # Disable all buttons to prevent multiple selections
        for btn in self.buttons.values():
            btn.setEnabled(False)
        
        # Check if the answer is correct
        if chosen_answer == self.correct_answer:
            # Correct answer - make the button green with stronger styling
            sender_button.setStyleSheet("background-color: #5cb85c; color: white; font-weight: bold; border: 2px solid #4cae4c; border-radius: 5px;")
            
            # Increment correct count
            self.correct_count += 1
            self.ui.lbl_correct_count.setText(str(self.correct_count))
            
            # Update the highest score if needed
            self.update_highest_score()
            
            # Show trivia about the correct answer
            if hasattr(self, 'current_trivia') and self.current_trivia:
                self.ui.lbl_trivia.setText(self.current_trivia)
                self.ui.lbl_trivia.setVisible(True)
                
                # Show pause button when trivia is displayed
                self.ui.btn_pause.setVisible(True)
        else:
            # Wrong answer - make the clicked button red with much more prominent styling
            sender_button.setStyleSheet("background-color: #d9534f; color: white; font-weight: bold; border: 2px solid #d43f3a; border-radius: 5px;")
            # Highlight the correct answer in green with stronger styling
            self.buttons[self.correct_answer].setStyleSheet("background-color: #5cb85c; color: white; font-weight: bold; border: 2px solid #4cae4c; border-radius: 5px;")
            
            # Increment incorrect count
            self.incorrect_count += 1
            self.ui.lbl_incorrect_count.setText(str(self.incorrect_count))
            
            # Show trivia about the correct answer even if wrong
            if hasattr(self, 'current_trivia') and self.current_trivia:
                self.ui.lbl_trivia.setText(self.current_trivia)
                self.ui.lbl_trivia.setVisible(True)
                
                # Show pause button when trivia is displayed
                self.ui.btn_pause.setVisible(True)
        
        # Force immediate UI refresh to ensure styling is applied
        QApplication.processEvents()
        
        # Enable the next button
        self.ui.btn_next.setEnabled(True)
        
        # Start the delay timer for automatic progression
        self.remaining_delay_time = 10000  # 10 seconds delay
        self.delay_timer.start(self.remaining_delay_time)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    quiz = QuizGame()
    sys.exit(app.exec())