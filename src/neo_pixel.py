import neopixel
import board

class NeoPixel:
  def __init__(self):
    pixels = neopixel.NeoPixel(board.D10, 5, brightness=0.3, auto_write=True)
    self.pixels = pixels

  def set_color(self, r, g, b):
    for i in range(len(self.pixels)):
      self.pixels[i] = (r, g, b)
