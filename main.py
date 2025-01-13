import cv2
import mediapipe as mp
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Initialize OpenCV Video Capture
cap = cv2.VideoCapture(0)

# Chessboard settings
board_width, board_height = 8, 8
chessboard_size = 400  # Size of the chessboard in pixels
chessboard_origin = (200, 200)  # Top-left corner of the chessboard on screen

# Initialize Selenium WebDriver (Chrome)
from selenium.webdriver.chrome.service import Service
service = Service('/Users/macbookpro/Documents/GitHub/PawnPal/chromedriver')  # Update this path to your chromedriver
driver = webdriver.Chrome(service=service)

driver.get('https://www.chess.com/play')  # Chess.com game page
time.sleep(5)  # Wait for the page to load

# Chessboard square mapping (8x8 grid)
square_mapping = {
    (0, 0): 'square-a1', (0, 1): 'square-b1', (0, 2): 'square-c1', (0, 3): 'square-d1',
    (0, 4): 'square-e1', (0, 5): 'square-f1', (0, 6): 'square-g1', (0, 7): 'square-h1',
    (1, 0): 'square-a2', (1, 1): 'square-b2', (1, 2): 'square-c2', (1, 3): 'square-d2',
    (1, 4): 'square-e2', (1, 5): 'square-f2', (1, 6): 'square-g2', (1, 7): 'square-h2',
    (2, 0): 'square-a3', (2, 1): 'square-b3', (2, 2): 'square-c3', (2, 3): 'square-d3',
    (2, 4): 'square-e3', (2, 5): 'square-f3', (2, 6): 'square-g3', (2, 7): 'square-h3',
    (3, 0): 'square-a4', (3, 1): 'square-b4', (3, 2): 'square-c4', (3, 3): 'square-d4',
    (3, 4): 'square-e4', (3, 5): 'square-f4', (3, 6): 'square-g4', (3, 7): 'square-h4',
    (4, 0): 'square-a5', (4, 1): 'square-b5', (4, 2): 'square-c5', (4, 3): 'square-d5',
    (4, 4): 'square-e5', (4, 5): 'square-f5', (4, 6): 'square-g5', (4, 7): 'square-h5',
    (5, 0): 'square-a6', (5, 1): 'square-b6', (5, 2): 'square-c6', (5, 3): 'square-d6',
    (5, 4): 'square-e6', (5, 5): 'square-f6', (5, 6): 'square-g6', (5, 7): 'square-h6',
    (6, 0): 'square-a7', (6, 1): 'square-b7', (6, 2): 'square-c7', (6, 3): 'square-d7',
    (6, 4): 'square-e7', (6, 5): 'square-f7', (6, 6): 'square-g7', (6, 7): 'square-h7',
    (7, 0): 'square-a8', (7, 1): 'square-b8', (7, 2): 'square-c8', (7, 3): 'square-d8',
    (7, 4): 'square-e8', (7, 5): 'square-f8', (7, 6): 'square-g8', (7, 7): 'square-h8'
}

# Map hand position to chessboard square
def map_to_chessboard(x, y):
    grid_x = int((x - chessboard_origin[0]) / (chessboard_size / board_width))
    grid_y = int((y - chessboard_origin[1]) / (chessboard_size / board_height))
    grid_x = max(0, min(board_width - 1, grid_x))
    grid_y = max(0, min(board_height - 1, grid_y))
    return grid_x, grid_y

# Function to highlight the square in the browser
def highlight_square_on_chessboard(board_x, board_y):
    try:
        # Find the chessboard square element based on the mapping
        square_id = square_mapping[(board_x, board_y)]
        square_elem = driver.find_element(By.CLASS_NAME, square_id)
        
        # JavaScript to highlight the square by adding a CSS class (e.g., change background color)
        driver.execute_script("""
            arguments[0].style.backgroundColor = 'rgba(255, 255, 0, 0.5)';  // Change background color to yellow
        """, square_elem)
        
        print(f"Highlighted square: {square_id}")
        
    except Exception as e:
        print(f"Error highlighting square: {e}")

# Function to remove highlight from all squares
def remove_highlights():
    try:
        # Remove highlights from all squares (reset background color)
        driver.execute_script("""
            const squares = document.querySelectorAll('[class^="square-"]');
            squares.forEach(square => {
                square.style.backgroundColor = '';  // Reset background color
            });
        """)
        
        print("Removed all highlights.")
        
    except Exception as e:
        print(f"Error removing highlights: {e}")

# Perform the move on Chess.com
def make_move(from_square, to_square):
    try:
        from_elem = driver.find_element(By.CLASS_NAME, square_mapping[from_square])
        from_elem.click()
        time.sleep(1)
        to_elem = driver.find_element(By.CLASS_NAME, square_mapping[to_square])
        to_elem.click()
    except Exception as e:
        print(f"Error during move: {e}")

# Gesture detection
def is_two_finger_gesture(landmarks):
    # Check the distance between index and middle fingers
    index_finger = landmarks.landmark[8]
    middle_finger = landmarks.landmark[12]
    distance = ((index_finger.x - middle_finger.x) ** 2 + (index_finger.y - middle_finger.y) ** 2) ** 0.5
    return distance < 0.1  # Adjust this threshold as needed

# Main loop for hand tracking and move automation
selected_square = None  # Variable to track selected square
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Optional: Mirror the frame for easier hand tracking
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB (required by MediaPipe)
    
    # Process the frame with MediaPipe
    result = hands.process(rgb_frame)

    # If hands are detected
    if result.multi_hand_landmarks:
        for landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks
            mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get the coordinates of the index finger tip (landmark 8)
            finger_tip = landmarks.landmark[8]  # Finger tip is at index 8
            x, y = int(finger_tip.x * frame.shape[1]), int(finger_tip.y * frame.shape[0])

            # Map the finger position to the chessboard square
            board_x, board_y = map_to_chessboard(x, y)
            print(f"Hand mapped to chessboard square: ({board_x}, {board_y})")

            # Highlight the square where the hand is pointing
            highlight_square_on_chessboard(board_x, board_y)

            # Logic for selecting and confirming moves (e.g., two-finger gesture)
            if is_two_finger_gesture(landmarks):
                if selected_square is None:
                    selected_square = (board_x, board_y)
                    print(f"Selected square: {selected_square}")
                else:
                    print(f"Move confirmed from {selected_square} to ({board_x}, {board_y})")
                    make_move(selected_square, (board_x, board_y))  # Make the move
                    selected_square = None  # Reset selection

    # Display the camera feed with hand landmarks
    cv2.imshow("Hand Tracking - PawnPal", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Remove highlights before quitting
remove_highlights()

# Release resources
cap.release()
cv2.destroyAllWindows()
driver.quit()
