import displayio
import busio
from adafruit_display_text import label
import i2cdisplaybus
import adafruit_displayio_ssd1306
import board
import terminalio


class Visuals:
  W = 128
  H = 64
  LANES = 4
  LANE_W = W // LANES
  HIT_Y = 56
  NOTE_W = LANE_W - 6
  NOTE_H = 6
  SPEED = 1.5 

  notes = []
  difficulty_names = ["Easy", "Medium", "Hard", "Custom"]

  def __init__(self, i2c):
    displayio.release_displays()

    display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=self.W, height=self.H)
    root = displayio.Group()
    display.root_group = root
    self.root = root

    self.background()
    self.note_group()
    self.ui()

  def center_text(self, text_label, line_number):
    """Helper function to center text horizontally and position vertically
    line_number: 0-4 for 5 lines evenly spaced on 64px height display"""
    text_width = text_label.bounding_box[2]
    text_label.x = (self.W - text_width) // 2
    # Calculate line height for 5 lines: 64 / 5 = 12.8, use 12
    line_height = 12
    text_label.y = (line_number * line_height) + 6  # offset by 6 since it's the middle of the line
  
  def background(self):
    # create the background bitmap and palette
    # we have black and white as the palette
    bg = displayio.Bitmap(self.W, self.H, 2)
    pal = displayio.Palette(2)
    pal[0] = 0x000000
    pal[1] = 0xFFFFFF

    # drawing the background black initially
    for x in range(self.W):
        for y in range(self.H):
            bg[x, y] = 0

    # drawing lane lines
    for i in range(1, self.LANES):
        x = i * self.LANE_W
        for y in range(self.H):
            bg[x, y] = 1

    # drawing hit line
    for x in range(self.W):
        bg[x, self.HIT_Y] = 1

    # rendering the bitmap using this palette
    bg_tile = displayio.TileGrid(bg, pixel_shader=pal)

    # add a layer of the background to the root group
    self.root.append(bg_tile)
    self.bg_tile = bg_tile
    
    # Hide background by default (show only during game)
    self.bg_tile.hidden = True

  def note_group(self):
    # next we create a group for the note that renders on top of the background
    note_group = displayio.Group()
    self.note_group = note_group
    self.root.append(note_group)

  def ui(self):
    # Create main UI group
    ui = displayio.Group()
    self.root.append(ui)
    self.ui_group = ui
    
    # Create all UI elements as class attributes
    score_label = label.Label(terminalio.FONT, text="", x=0, y=6)
    miss_label = label.Label(terminalio.FONT, text="", x=0, y=16)
    level_label = label.Label(terminalio.FONT, text="", x=77, y=6)  # Moved left from 90 to 70
    
    # Menu elements
    menu_title = label.Label(terminalio.FONT, text="RHYTHM GAME")
    difficulty_easy = label.Label(terminalio.FONT, text="Easy")
    difficulty_medium = label.Label(terminalio.FONT, text="Medium")
    difficulty_hard = label.Label(terminalio.FONT, text="Hard")
    difficulty_custom = label.Label(terminalio.FONT, text="Custom")
    
    # Game over elements
    gameover_title = label.Label(terminalio.FONT, text="")
    gameover_result = label.Label(terminalio.FONT, text="")
    gameover_final_score = label.Label(terminalio.FONT, text="")
    gameover_final_misses = label.Label(terminalio.FONT, text="")
    gameover_restart = label.Label(terminalio.FONT, text="")
    
    # Position menu elements
    self.center_text(menu_title, 0)
    self.center_text(difficulty_easy, 1)
    self.center_text(difficulty_medium, 2)
    self.center_text(difficulty_hard, 3)
    self.center_text(difficulty_custom, 4)
    
    # Position game over elements
    self.center_text(gameover_title, 0)
    self.center_text(gameover_result, 1)
    self.center_text(gameover_final_score, 2)
    self.center_text(gameover_final_misses, 3)
    self.center_text(gameover_restart, 4)
    
    # Add all elements to UI group
    ui.append(score_label)
    ui.append(miss_label)
    ui.append(level_label)
    ui.append(menu_title)
    ui.append(difficulty_easy)
    ui.append(difficulty_medium)
    ui.append(difficulty_hard)
    ui.append(difficulty_custom)
    ui.append(gameover_title)
    ui.append(gameover_result)
    ui.append(gameover_final_score)
    ui.append(gameover_final_misses)
    ui.append(gameover_restart)
    
    # Store as class attributes
    self.score_label = score_label
    self.miss_label = miss_label
    self.level_label = level_label
    self.menu_title = menu_title
    self.difficulty_options = [difficulty_easy, difficulty_medium, difficulty_hard, difficulty_custom]
    self.gameover_elements = [gameover_title, gameover_result, gameover_final_score, gameover_final_misses, gameover_restart]

  # function to spawn a note in a given lane (only spawn at the top of the screen)
  def spawn_note_in_lane(self, lane, note_type="tap"):
    # figure out x and y position offset by 3 since note_w is smaller than lane_w by 6
    x = (lane - 1) * self.LANE_W + 3
    y = 0

    # create bitmap and tilegrid for the note
    bm = displayio.Bitmap(self.NOTE_W, self.NOTE_H, 2)
    pal2 = displayio.Palette(2)
    pal2[0] = 0x000000
    pal2[1] = 0xFFFFFF

    # render the bitmap using this palette at x and y 
    # (we're rendering from the top left corner)
    tile = displayio.TileGrid(bm, pixel_shader=pal2, x=x, y=y)

    # Different visual patterns for different note types
    if note_type == "flick":
      # Flick notes: hollow rectangle with arrow pattern
      # Draw border
      for bitmap_x in range(self.NOTE_W):
        bm[bitmap_x, 0] = 1  # top
        bm[bitmap_x, self.NOTE_H-1] = 1  # bottom
      for bitmap_y in range(self.NOTE_H):
        bm[0, bitmap_y] = 1  # left
        bm[self.NOTE_W-1, bitmap_y] = 1  # right
      
      # Draw upward arrow pattern in middle (if note is tall enough)
      if self.NOTE_H >= 5:
        mid_x = self.NOTE_W // 2
        bm[mid_x, 2] = 1  # arrow tip
        if self.NOTE_W >= 5:
          bm[mid_x-1, 3] = 1  # left wing
          bm[mid_x+1, 3] = 1  # right wing
    else:
      # Regular tap notes: solid rectangle
      for bitmap_x in range(self.NOTE_W):
        for bitmap_y in range(self.NOTE_H):
          bm[bitmap_x, bitmap_y] = 1

    # add the note to the notes array and the note group
    self.notes.append({"lane": lane - 1, "y": y, "sprite": tile, "type": note_type})
    # add the note sprite to the note group for rendering
    self.note_group.append(tile)

  # update the notes falling
  def update_notes(self):
    missed = 0
    # update position of each active note to move down with speed
    for note in self.notes[:]:
        # calculate new position and render it
        note["y"] += self.SPEED
        note["sprite"].y = int(note["y"])

        # check if the note has gone past the hit line (missed)
        if note["y"] > self.H:
            self.note_group.remove(note["sprite"])
            self.notes.remove(note)
            missed += 1
    return missed
  
  def note_hit(self, lane, is_flick=False):
    # update the global score variable
    for note in self.notes:
        # if the note is in the correct lane
        if note["lane"] == lane:
            # check if the note is within the hit window
            note_center = note["y"] + self.NOTE_H / 2
            
            # Flick notes get 1.5x larger hit window
            hit_window = self.NOTE_H / 2
            if note["type"] == "flick":
                hit_window *= 1.5
            
            if self.HIT_Y - hit_window <= note_center <= self.HIT_Y + hit_window:
                # Check if input type matches note type
                if (note["type"] == "flick" and is_flick) or (note["type"] == "tap" and not is_flick):
                    # if it hit we remove the note from the screen and active notes
                    self.note_group.remove(note["sprite"])
                    self.notes.remove(note)
                    return True
    return False
  
  # update score and misses UI
  def update_ui(self, score, miss, level=1):
    self.score_label.text = "Score: {}".format(score)
    self.miss_label.text = "Miss: {}".format(miss)
    self.level_label.text = "Level: {}".format(level)
  
  def set_difficulty(self, difficulty_index):
    """Set note height based on difficulty: 0=Easy(10px), 1=Medium(8px), 2=Hard(6px), 3=Custom(6px)"""
    if difficulty_index == 0:  # Easy
      self.NOTE_H = 12
    elif difficulty_index == 1:  # Medium
      self.NOTE_H = 9
    elif difficulty_index == 2:  # Hard
      self.NOTE_H = 6
    else:  # Custom
      self.NOTE_H = 6
    print(f"Difficulty set to {self.difficulty_names[difficulty_index]}, Note height: {self.NOTE_H}px")

  def show_menu(self, difficulty_index=0):
    # Hide game elements
    self.score_label.text = ""
    self.miss_label.text = ""
    self.level_label.text = ""
    self.bg_tile.hidden = True
    
    # Hide game over elements
    for element in self.gameover_elements:
      element.hidden = True
    
    # Show menu elements
    self.menu_title.hidden = False
    for option in self.difficulty_options:
      option.hidden = False
    
    # Highlight selected difficulty and re-center text
    for i, option in enumerate(self.difficulty_options):
      if i == difficulty_index:
        option.text = "> " + self.difficulty_names[i] + " <"
      else:
        option.text = self.difficulty_names[i]
      # Re-center the text after updating it
      self.center_text(option, i + 1)

  def show_game(self):
    # Hide menu elements
    self.menu_title.hidden = True
    for option in self.difficulty_options:
      option.hidden = True
    
    # Hide game over elements
    for element in self.gameover_elements:
      element.hidden = True
    
    # Show background lanes/hit line
    self.bg_tile.hidden = False
    
    # Score/miss labels will be updated by update_ui() calls
  
  def show_gameover(self, game_result, final_score, final_misses):
    # Hide game elements
    self.score_label.text = ""
    self.miss_label.text = ""
    self.level_label.text = ""
    self.bg_tile.hidden = True
    
    # Hide menu elements
    self.menu_title.hidden = True
    for option in self.difficulty_options:
      option.hidden = True
    
    # Show and update game over elements
    for element in self.gameover_elements:
      element.hidden = False
    
    # Update game over text
    self.gameover_elements[0].text = "GAME OVER"
    if game_result == "win":
      self.gameover_elements[1].text = "YOU WIN!"
    else:
      self.gameover_elements[1].text = "YOU LOSE!"
    
    self.gameover_elements[2].text = f"Score: {final_score}"
    self.gameover_elements[3].text = f"Misses: {final_misses}"
    self.gameover_elements[4].text = "Press any button"
    
    # Re-center text after updating
    self.center_text(self.gameover_elements[0], 0)
    self.center_text(self.gameover_elements[1], 1)
    self.center_text(self.gameover_elements[2], 2)
    self.center_text(self.gameover_elements[3], 3)
    self.center_text(self.gameover_elements[4], 4)
