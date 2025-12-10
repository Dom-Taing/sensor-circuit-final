import neopixel
import board

class NeoPixel:
  def __init__(self):
    pixels = neopixel.NeoPixel(board.D10, 1, brightness=0.3, auto_write=True)
    self.pixels = pixels

  def set_color(self, r, g, b):
    self.pixels[0] = (r, g, b)

