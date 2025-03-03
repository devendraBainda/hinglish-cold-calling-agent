import pygame
import time
import os
from datetime import datetime

import utils
from system_prompts import SYSTEM_PROMPTS
from recording_helper import RecordingHelper

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 50, 150)

# Define screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=DARK_BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        # Draw button with hover effect
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2, border_radius=5)
        
        # Draw text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder='Enter text...'):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.text = text
        self.placeholder = placeholder
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = BLUE if self.active else GRAY
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        return None
    
    def draw(self, screen, font):
        # Draw the input box
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=5)
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)
        
        # Draw text or placeholder
        if self.text:
            text_surface = font.render(self.text, True, BLACK)
        else:
            text_surface = font.render(self.placeholder, True, DARK_GRAY)
            
        # Position text
        text_rect = text_surface.get_rect(topleft=(self.rect.x + 5, self.rect.y + 5))
        
        # Make sure text doesn't go beyond the box
        if text_rect.width > self.rect.width - 10:
            screen.blit(text_surface, text_rect, pygame.Rect(text_rect.width - (self.rect.width - 10), 0, self.rect.width - 10, text_rect.height))
        else:
            screen.blit(text_surface, text_rect)
            
    def get_text(self):
        return self.text

class ScrollableTextArea:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.scroll_y = 0
        self.line_height = 24
        self.visible_lines = height // self.line_height
        self.lines = []
        self.max_chars_per_line = width // 10  # Approximate
        
    def add_text(self, speaker, text):
        # Format text with speaker and timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_text = f"[{timestamp}] {speaker}: {text}"
        
        # Wrap text to fit the width
        words = new_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= self.max_chars_per_line:
                current_line += (word + " ")
            else:
                lines.append(current_line)
                current_line = word + " "
        
        if current_line:
            lines.append(current_line)
            
        self.lines.extend(lines)
        
        # Auto-scroll to bottom
        if len(self.lines) > self.visible_lines:
            self.scroll_y = len(self.lines) - self.visible_lines
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - 1)
            elif event.button == 5:  # Scroll down
                self.scroll_y = min(max(0, len(self.lines) - self.visible_lines), self.scroll_y + 1)
                
    def draw(self, screen, font):
        # Draw background
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=5)
        pygame.draw.rect(screen, GRAY, self.rect, 2, border_radius=5)
        
        # Create a clip area
        screen.set_clip(self.rect)
        
        # Draw visible lines
        start_line = self.scroll_y
        end_line = min(start_line + self.visible_lines, len(self.lines))
        
        for i, line in enumerate(self.lines[start_line:end_line]):
            y_pos = self.rect.y + (i * self.line_height) + 5
            
            # Color coding for different speakers
            if "AI:" in line:
                text_color = BLUE
            elif "You:" in line:
                text_color = GREEN
            else:
                text_color = BLACK
                
            text_surface = font.render(line, True, text_color)
            screen.blit(text_surface, (self.rect.x + 5, y_pos))
        
        # Draw scrollbar if needed
        if len(self.lines) > self.visible_lines:
            scrollbar_height = self.rect.height * (self.visible_lines / len(self.lines))
            scrollbar_pos = self.rect.y + (self.scroll_y / (len(self.lines) - self.visible_lines)) * (self.rect.height - scrollbar_height)
            
            scrollbar_rect = pygame.Rect(self.rect.right - 15, scrollbar_pos, 10, scrollbar_height)
            pygame.draw.rect(screen, DARK_GRAY, scrollbar_rect, border_radius=5)
        
        # Reset clip area
        screen.set_clip(None)

class AIAssistantApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hinglish Cold Calling AI Agent")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 42)
        self.normal_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        # App state
        self.current_state = "scenario_selection"  # States: scenario_selection, conversation
        self.scenario = None
        self.user_email = ""
        self.is_recording = False
        self.recording_start_time = 0
        
        # Speech recognition
        self.recording_helper = RecordingHelper()
        
        # Create UI elements - Scenario Selection
        self.demo_button = Button(SCREEN_WIDTH//2-150, 200, 300, 50, "Demo Scheduling for ERP System")
        self.interview_button = Button(SCREEN_WIDTH//2-150, 270, 300, 50, "Candidate Interviewing")
        self.payment_button = Button(SCREEN_WIDTH//2-150, 340, 300, 50, "Payment/Order Follow-up")
        self.email_input = InputBox(SCREEN_WIDTH//2-150, 410, 300, 40, "", "Enter email address...")
        
        # Create UI elements - Conversation
        self.conversation_area = ScrollableTextArea(50, 100, SCREEN_WIDTH-100, 400)
        self.record_button = Button(SCREEN_WIDTH//2-100, SCREEN_HEIGHT-80, 200, 50, "Start Recording (SPACE)")
        self.exit_button = Button(SCREEN_WIDTH-150, SCREEN_HEIGHT-80, 100, 50, "Exit")
        self.back_button = Button(50, SCREEN_HEIGHT-80, 100, 50, "Back")
        
        # Recording animation
        self.recording_dots = 0
        self.recording_anim_time = 0
    
    def draw_scenario_selection(self):
        """Draw the scenario selection screen"""
        self.screen.fill(LIGHT_GRAY)
        
        # Draw title
        title_surf = self.title_font.render("Hinglish Cold Calling AI Agent", True, DARK_BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Draw subtitle
        subtitle_surf = self.normal_font.render("Select a scenario to begin:", True, BLACK)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH//2, 130))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Draw buttons
        self.demo_button.draw(self.screen, self.normal_font)
        self.interview_button.draw(self.screen, self.normal_font)
        self.payment_button.draw(self.screen, self.normal_font)
        
        # Draw email input label
        email_label = self.normal_font.render("Email Address:", True, BLACK)
        self.screen.blit(email_label, (SCREEN_WIDTH//2-150, 385))
        
        # Draw email input
        self.email_input.draw(self.screen, self.normal_font)
        
        # Draw footer
        footer_surf = self.small_font.render("Press ESC to exit application", True, DARK_GRAY)
        footer_rect = footer_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-30))
        self.screen.blit(footer_surf, footer_rect)
    
    def draw_conversation(self):
        """Draw the conversation screen"""
        self.screen.fill(LIGHT_GRAY)
        
        # Draw title with scenario
        scenario_name = {
            "demo_scheduling": "Demo Scheduling",
            "candidate_interviewing": "Candidate Interviewing",
            "payment_followup": "Payment/Order Follow-up"
        }.get(self.scenario, "Conversation")
        
        title_surf = self.title_font.render(f"AI Agent: {scenario_name}", True, DARK_BLUE)
        title_rect = title_surf.get_rect(midleft=(50, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Draw email info
        email_surf = self.small_font.render(f"Email: {self.user_email}", True, DARK_GRAY)
        email_rect = email_surf.get_rect(midright=(SCREEN_WIDTH-50, 50))
        self.screen.blit(email_surf, email_rect)
        
        # Draw conversation area
        self.conversation_area.draw(self.screen, self.small_font)
        
        # Draw buttons
        self.record_button.draw(self.screen, self.normal_font)
        self.exit_button.draw(self.screen, self.normal_font)
        self.back_button.draw(self.screen, self.normal_font)
        
        # Draw recording indicator if recording
        if self.is_recording:
            # Update animation
            current_time = time.time()
            if current_time - self.recording_anim_time > 0.5:
                self.recording_dots = (self.recording_dots + 1) % 4
                self.recording_anim_time = current_time
                
            dots = "." * self.recording_dots
            recording_surf = self.normal_font.render(f"Recording{dots}", True, RED)
            recording_rect = recording_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-120))
            self.screen.blit(recording_surf, recording_rect)
            
            # Draw recording time
            elapsed = int(time.time() - self.recording_start_time)
            time_surf = self.small_font.render(f"Time: {elapsed}s", True, DARK_GRAY)
            time_rect = time_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-100))
            self.screen.blit(time_surf, time_rect)
    
    def switch_to_conversation(self):
        """Switch to conversation mode"""
        self.current_state = "conversation"
        
        # Default email for candidate interviewing
        if self.scenario == "candidate_interviewing":
            self.user_email = "candidate@example.com"
        elif not self.user_email:
            self.user_email = "customer@example.com"
        
        # Prepare initial greeting
        initial_greeting = {
            "demo_scheduling": "Namaste! Mai iMax Global Ventures se bol raha hoon. Kya aap hamare ERP system ke baare mein baat karna chahenge?",
            "candidate_interviewing": "Namaste! Mai iMax Global Ventures se bol raha hoon. Hum aapka interview lene wale hain AI/ML Engineer position ke liye.",
            "payment_followup": "Namaste! Mai iMax Global Ventures se bol raha hoon. Mai aapke pending payment ke baare mein baat karna chahta hoon."
        }
        
        greeting = initial_greeting.get(self.scenario, "Namaste! Mai iMax Global Ventures se bol raha hoon.")
        
        # Add greeting to conversation
        self.conversation_area.add_text("AI", greeting)
        
        # Synthesize and play greeting
        greeting_audio = utils.synthesize_speech(greeting, output_path="greeting.mp3")
        utils.play_audio(greeting_audio)
    
    def start_recording(self):
        """Start recording audio"""
        if self.recording_helper.start_recording():
            self.is_recording = True
            self.recording_start_time = time.time()
            self.record_button.text = "Stop Recording (SPACE)"
        else:
            self.conversation_area.add_text("System", "Could not start recording. Please try again.")
            
    def recognize_speech(self):
        """Get the recognized speech from our helper"""
        self.recording_helper.stop_recording()
        
        # Wait a bit for the processing to complete
        wait_time = 0
        while not self.recording_helper.is_complete and wait_time < 30:
            pygame.time.delay(100)  # Wait for 100ms
            wait_time += 0.1
            
            # Need to keep the UI responsive during waiting
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
        
        text, error = self.recording_helper.get_result()
        
        if error:
            self.conversation_area.add_text("System", f"Error: {error}")
            
        return text
    
    def stop_recording(self):
        """Stop recording and process audio"""
        self.is_recording = False
        self.record_button.text = "Start Recording (SPACE)"
        
        # Show Processing message
        processing_surf = self.normal_font.render("Processing...", True, GREEN)
        processing_rect = processing_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-120))
        self.screen.blit(processing_surf, processing_rect)
        pygame.display.flip()
        
        # Get recognized text using our own recording method instead of utils function
        recognized_text = self.recognize_speech()
        
        if recognized_text:
            # Add user's text to conversation
            self.conversation_area.add_text("You", recognized_text)
            
            # Process based on scenario
            if recognized_text.lower() in ["exit", "quit", "stop", "बंद", "बंद करो"]:
                self.current_state = "scenario_selection"
                return
            
            # Get AI response based on scenario
            if self.scenario == "demo_scheduling":
                ai_response = utils.handle_demo_scheduling(self.user_email, recognized_text)
            elif self.scenario == "candidate_interviewing":
                ai_response = utils.handle_candidate_interview(recognized_text)
            elif self.scenario == "payment_followup":
                ai_response = utils.handle_payment_followup(self.user_email, recognized_text)
            else:
                ai_response = utils.get_ai_response(recognized_text)
            
            # Add AI response to conversation
            self.conversation_area.add_text("AI", ai_response)
            
            # Synthesize speech and play audio
            audio_file = utils.synthesize_speech(ai_response)
            utils.play_audio(audio_file)
        else:
            self.conversation_area.add_text("System", "Could not understand audio. Please try again.")
    
    def run(self):
        """Main application loop"""
        running = True
        
        while running:
            # Track mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Make sure to stop any active recording before quitting
                    if self.is_recording:
                        self.recording_helper.stop_recording()
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_state == "scenario_selection":
                            running = False
                        else:
                            # Make sure to stop any active recording before going back
                            if self.is_recording:
                                self.recording_helper.stop_recording()
                                self.is_recording = False
                            self.current_state = "scenario_selection"
                    
                    if event.key == pygame.K_SPACE and self.current_state == "conversation":
                        if self.is_recording:
                            self.stop_recording()
                        else:
                            self.start_recording()
                
                # Handle state-specific events
                if self.current_state == "scenario_selection":
                    # Handle input box events
                    self.email_input.handle_event(event)
                    
                    # Handle button clicks
                    if self.demo_button.is_clicked(mouse_pos, event):
                        self.scenario = "demo_scheduling"
                        self.user_email = self.email_input.get_text()
                        self.switch_to_conversation()
                    
                    elif self.interview_button.is_clicked(mouse_pos, event):
                        self.scenario = "candidate_interviewing"
                        self.user_email = "candidate@example.com"
                        self.switch_to_conversation()
                    
                    elif self.payment_button.is_clicked(mouse_pos, event):
                        self.scenario = "payment_followup"
                        self.user_email = self.email_input.get_text()
                        self.switch_to_conversation()
                
                elif self.current_state == "conversation":
                    # Handle scrollable text area events
                    self.conversation_area.handle_event(event)
                    
                    # Handle button clicks
                    if self.record_button.is_clicked(mouse_pos, event):
                        if self.is_recording:
                            self.stop_recording()
                        else:
                            self.start_recording()
                    
                    elif self.exit_button.is_clicked(mouse_pos, event):
                        running = False
                    
                    elif self.back_button.is_clicked(mouse_pos, event):
                        self.current_state = "scenario_selection"
            
            # Update button hover states
            if self.current_state == "scenario_selection":
                self.demo_button.check_hover(mouse_pos)
                self.interview_button.check_hover(mouse_pos)
                self.payment_button.check_hover(mouse_pos)
            else:
                self.record_button.check_hover(mouse_pos)
                self.exit_button.check_hover(mouse_pos)
                self.back_button.check_hover(mouse_pos)
            
            # Draw the current state
            if self.current_state == "scenario_selection":
                self.draw_scenario_selection()
            else:
                self.draw_conversation()
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(60)        
        pygame.quit()

def run_ui():
    """Run the PyGame UI application"""
    try:
        app = AIAssistantApp()
        app.run()
    except Exception as e:
        print(f"Error in PyGame UI: {e}")      
        pygame.quit()

# Testing the UI
if __name__ == "__main__":
    run_ui()