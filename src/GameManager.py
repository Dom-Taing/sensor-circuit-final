import time
import board
import digitalio
from audio import AudioPlayer
from visual import Visuals
from rotary_encoder import RotaryEncoder 
from neo_pixel import NeoPixel
from accelerometer import Accelerometer

class GameManager:
  def __init__(self):
    # set up audio and visuals
    self.audio = AudioPlayer()
    i2c = board.I2C() 
    self.visual = Visuals(i2c)
    self.accelerometer = Accelerometer(i2c)
    
    # set up buttons
    pins = [board.D2, board.D3, board.D8, board.D9]
    buttons = []
    for p in pins:
        # creates a digital I/O object for each button
        b = digitalio.DigitalInOut(p)
        # tells the microcontroller that we're reading input not giving output for this pin
        b.direction = digitalio.Direction.INPUT
        # activate the internal pull-up resistor on the pin
        b.pull = digitalio.Pull.UP
        # add the button to the array so that we can reference it later
        buttons.append(b)
    self.buttons = buttons
    self.buttons_prev_state = [True] * len(buttons)

    # set up rotary encoder
    encoder = RotaryEncoder(board.D0, board.D1, debounce_ms=3, pulses_per_detent=3)
    self.rotary_encoder = encoder
    self.rotary_position = encoder.position

    # set up neo_pixels
    self.pixels = NeoPixel()

    # beat map and game state
    self.beat_map = []
    self.beat_index = 0
    self.score = 0
    self.misses = 0
    
    # Level system
    self.current_level = 1
    self.max_level = 10
    self.level_beat_counts = []  # Will store how many beats per level
    self.level_start_indices = []  # Will store starting beat index for each level
    self.completed_beats = 0  # Track beats that have been hit or missed

    # Game states
    self.state = "menu"  # can be: "menu", "playing", "gameover", "loading"
    self.game_result = None  # "win" or "lose"
    
    # Menu state variables
    self.difficulty = 0  # 0=easy, 1=medium, 2=hard, 3=custom
    self.difficulties = ["Easy", "Medium", "Hard", "Custom"]

    self.song_start = 0

    FPS = 30 # frames per second
    SPEED = 1.5 # pixel per frame
    HIT_Y = 56
    self.FPS = FPS
    self.FALL_TIME = HIT_Y / (SPEED * FPS)

    self.last_input_update = 0
    self.visual_update = 0
    self.input_interval = 0.005 # maybe we should use 0.003
    self.visual_interval = 1 / FPS
    time.sleep(1)

  def start_game(self, track):
    self.beat_index = 0
    self.score = 0
    self.misses = 0
    self.current_level = 1
    self.completed_beats = 0
    self.game_result = None
    self.state = "playing"
    
    # Set difficulty-based note height
    self.visual.set_difficulty(self.difficulty)
    
    self.visual.show_game()
    self.audio.play(track)
    self.song_start = time.monotonic()
    
    print(f"Starting Level {self.current_level} with {self.level_beat_counts[0]} beats")

  def assign_beat_map(self, beat_map):
    self.beat_map = beat_map
    self.calculate_level_distribution()
  
  def calculate_level_distribution(self):
    """Calculate how many beats each level should have - total 100% distributed progressively"""
    total_beats = len(self.beat_map)
    self.level_beat_counts = []
    self.level_start_indices = []
    
    # Progressive distribution: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 parts
    # Total parts = 1+2+3+4+5+6+7+8+9+10 = 55 parts
    total_parts = sum(range(1, self.max_level + 1))
    
    cumulative_beats = 0
    for level in range(1, self.max_level + 1):
      parts_for_level = level  # Level 1 gets 1 part, Level 2 gets 2 parts, etc.
      beats_for_level = max(1, int(total_beats * parts_for_level / total_parts))
      
      self.level_start_indices.append(cumulative_beats)
      self.level_beat_counts.append(beats_for_level)
      cumulative_beats += beats_for_level
      
      percentage = (parts_for_level / total_parts) * 100
      print(f"Level {level}: {beats_for_level} beats ({percentage:.1f}%) - Start index: {self.level_start_indices[-1]}")
    
    # Add any leftover beats to level 10
    leftover_beats = total_beats - cumulative_beats
    if leftover_beats > 0:
      self.level_beat_counts[-1] += leftover_beats
      print(f"Added {leftover_beats} leftover beats to Level 10. New count: {self.level_beat_counts[-1]}")
    
    print(f"Total beats distributed: {sum(self.level_beat_counts)}/{total_beats}")
  
  def check_clicks(self):
    clicked = [False] * len(self.buttons)
    for i, button in enumerate(self.buttons):
      pressed = not button.value # active low
      was_pressed = not self.buttons_prev_state[i]
      if pressed and was_pressed:
        clicked[i] = True
      self.buttons_prev_state[i] = pressed
    return clicked
  
  def check_rotary_menu(self):
    changed = self.rotary_encoder.update()
    if changed:
      print("Position:", self.rotary_encoder.position)
      # In menu: change difficulty selection using position
      self.difficulty = self.rotary_encoder.position % len(self.difficulties)
      print(f"Difficulty: {self.difficulties[self.difficulty]}")
  
  def check_rotary_playing(self):
    changed = self.rotary_encoder.update()
    if changed:
      # In game: change volume using delta
      delta = self.rotary_encoder.get_delta()
      print("Rotary Delta:", delta)
      if delta > 0:
        print("increase volume")
        for _ in range(abs(delta)):  # Handle multiple steps
          self.audio.increase_volume()
      elif delta < 0:
        print("decrease volume")
        for _ in range(abs(delta)):  # Handle multiple steps
          self.audio.decrease_volume()
  
  def update(self):
    if self.state == "":
      return

    now = time.monotonic()

    if (now - self.last_input_update) >= self.input_interval:
      clicked = self.check_clicks()
      
      if self.state == "menu":
        self.check_rotary_menu()
        self.handle_menu_input(clicked)
      elif self.state == "playing":
        self.check_rotary_playing()
        self.handle_playing_input(clicked, now)
      elif self.state == "gameover":
        self.handle_gameover_input(clicked)
      
      self.last_input_update = now
      
    if (now - self.visual_update) >= self.visual_interval:
      if self.state == "menu":
        self.update_menu_display()
      elif self.state == "playing":
        self.update_game_display(now)
      elif self.state == "gameover":
        self.update_gameover_display()
      
      self.visual_update = now

  def handle_menu_input(self, clicked):
    # Any button: Start game
    for i, was_clicked in enumerate(clicked):
      if was_clicked:
        self.start_game(track=1)
        break  # Only need to start once even if multiple buttons pressed

  def handle_playing_input(self, clicked, now):
    song_now = now - self.song_start
    
    # Handle button presses (tap notes)
    for i, was_clicked in enumerate(clicked):
      if was_clicked:
        if self.visual.note_hit(i, is_flick=False):  # Tap input
          self.score += 1
          self.completed_beats += 1  # Track completed beat
          self.pixels.set_color(0,255,0)
    
    # Handle flick motion (flick notes)
    isFlicked = self.accelerometer.detect_flick()
    if isFlicked:
      print("Flick detected!")
      # Check all lanes for flick notes
      hit_any_flick = False
      for lane in range(4):
        if self.visual.note_hit(lane, is_flick=True):  # Flick input
          self.score += 1
          self.completed_beats += 1
          self.pixels.set_color(0,255,0)
          hit_any_flick = True
          break

  def update_menu_display(self):
    # Clear any notes from previous game
    self.visual.notes.clear()
    for child in self.visual.note_group:
      self.visual.note_group.remove(child)
    
    # Display difficulty selection on screen
    self.visual.show_menu(self.difficulty)

  def update_game_display(self, now):
    song_now = now - self.song_start
    
    # Spawn notes early so they land on the beat
    while self.beat_index < len(self.beat_map):
      beat_data = self.beat_map[self.beat_index]
      
      # Handle both old format (time, lane) and new format (time, lane, type)
      if len(beat_data) == 2:
        beat_time, lane = beat_data
        note_type = "tap"  # Default to tap for old beatmaps
      else:
        beat_time, lane, note_type = beat_data
      
      spawn_time = beat_time - self.FALL_TIME

      if song_now >= spawn_time:
        self.visual.spawn_note_in_lane(lane, note_type)
        self.beat_index += 1
      else:
        break

    missed_now = self.visual.update_notes()
    if (missed_now > 0):
      self.pixels.set_color(255,0,0)
    self.misses += missed_now
    self.completed_beats += missed_now  # Track missed beats as completed too
    
    # Check for lose condition (more than 10 misses)
    if self.misses > 10:
      self.game_result = "lose"
      self.state = "gameover"
      print(f"Game Over - You Lose! Misses: {self.misses}")
      return
    
    # Check for win condition (all beats completed)
    if self.completed_beats >= len(self.beat_map):
      self.game_result = "win"
      self.state = "gameover"
      print(f"Game Over - You Win! Score: {self.score}, Misses: {self.misses}")
      return
    
    # Check for level progression based on completed beats
    if self.current_level <= self.max_level:
      level_end_beats = self.level_start_indices[self.current_level - 1] + self.level_beat_counts[self.current_level - 1]
      
      # If we've completed current level's beats, advance to next level
      if self.completed_beats >= level_end_beats and self.current_level < self.max_level:
        self.current_level += 1
        print(f"Level Up! Now on Level {self.current_level} with {self.level_beat_counts[self.current_level - 1]} beats")
        print(f"Completed beats: {self.completed_beats}")
    
    self.visual.update_ui(self.score, self.misses, self.current_level)

  def handle_gameover_input(self, clicked):
    # Any button: Return to menu
    for i, was_clicked in enumerate(clicked):
      if was_clicked:
        self.state = "menu"
        print("Returning to menu...")
        break
  
  def update_gameover_display(self):
    # Clear any remaining notes
    self.visual.notes.clear()
    for child in self.visual.note_group:
      self.visual.note_group.remove(child)
    
    # Show game over screen with results
    self.visual.show_gameover(self.game_result, self.score, self.misses)

