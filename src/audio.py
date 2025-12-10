import time
import busio
import board

class AudioPlayer:

  # we're using tx and rx pin D6 and D7 respectively
  # we're communicating at 9600 bit per second
  def __init__(self):
    self.uart = busio.UART(board.D7, board.D6, baudrate=9600, timeout=1)
    self.volume(20)  # set default volume to 20

  def _send(self, cmd, param=0):
    # our param need to be converted into 2 bytes
    high = param // 256
    low = param % 256

    # check sum so that the dfplayer can check whether it have received all our command correctly
    checksum = 0xFFFF - (0xFF + 0x06 + cmd + 0x00 + 0x00 + high + low) + 1

    # our message to send to the dfplayer
    msg = bytearray([
        0x7E, 0xFF, 0x06, cmd, 0x00,
        high, low,
        (checksum >> 8) & 0xFF,
        checksum & 0xFF,
        0xEF
    ])

    # send the message via to the dfplayer
    self.uart.write(msg)

  # DATA-SHEET: https://picaxe.com/docs/spe033.pdf
  # track selection
  def play(self, track):
    self._send(0x03, track)
  def next_track(self):
    self._send(0x01)
  def previous_track(self):
    self._send(0x02)
  
  # playback control
  def pause(self):
    self._send(0x0E)
  def resume(self):
    self._send(0x0D)
  def stop(self):
    pass

  # volume
  def volume(self, level):
    self._send(0x06, level)
  def increase_volume(self):
    self._send(0x04)
  def decrease_volume(self):
    self._send(0x05)

