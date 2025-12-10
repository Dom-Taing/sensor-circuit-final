import busio
import board
import adafruit_adxl34x
import time
import displayio

class Accelerometer:
  def __init__(self, i2c):
    self.accelerometer = adafruit_adxl34x.ADXL345(i2c)
    self.accelerometer.range = adafruit_adxl34x.Range.RANGE_4_G
    
    # Zero-offset calibration (you already have this!)
    samples = [self.accelerometer.acceleration[2] for _ in range(20)]
    self.baseline_z = sum(samples) / len(samples)
    
    # Low-pass filter for noise reduction
    self.filtered_z = self.baseline_z
    self.alpha_lowpass = 0.6  # Optimized smoothing factor for low-pass (0-1, lower = more smoothing)
    
    # High-pass IIR filter for motion isolation
    self.prev_raw_z = self.baseline_z
    self.highpass_z = 0.0
    self.alpha_highpass = 0.92  # Much more conservative high-pass filter
    
    self.flick_threshold = 1.5    # Much higher threshold - requires strong intentional flicks
    self.cooldown = 0.4 # seconds before detecting again
    self.last_flick = 0
  
  def apply_lowpass_filter(self, raw_value):
    """Apply low-pass filter to reduce high-frequency noise"""
    self.filtered_z = self.alpha_lowpass * raw_value + (1 - self.alpha_lowpass) * self.filtered_z
    return self.filtered_z
  
  def apply_highpass_filter(self, raw_signal):
    """Apply first-order IIR high-pass filter: signalFiltered = alpha * (signalFiltered + rawSignal - rawSignalPrevious)"""
    self.highpass_z = self.alpha_highpass * (self.highpass_z + raw_signal - self.prev_raw_z)
    self.prev_raw_z = raw_signal
    return self.highpass_z
  
  def detect_flick(self):
    x, y, z = self.accelerometer.acceleration
    now = time.monotonic()

    # Apply low-pass filter first to reduce noise
    lowpass_z = self.apply_lowpass_filter(z)
    
    # Apply IIR high-pass filter to isolate quick movements
    highpass_z = self.apply_highpass_filter(lowpass_z)
    
    # Check for flick using high-pass filtered value (detects quick upward motion)
    if highpass_z > self.flick_threshold and now - self.last_flick > self.cooldown:
      self.last_flick = now
      return True

    return False
  
  def tune_parameters(self, lowpass_alpha=None, highpass_alpha=None, threshold=None):
    """Helper function to quickly tune filter parameters"""
    if lowpass_alpha is not None:
      self.alpha_lowpass = lowpass_alpha
      print(f"Low-pass alpha set to: {self.alpha_lowpass}")
    
    if highpass_alpha is not None:
      self.alpha_highpass = highpass_alpha
      print(f"High-pass alpha set to: {self.alpha_highpass}")
    
    if threshold is not None:
      self.flick_threshold = threshold
      print(f"Flick threshold set to: {self.flick_threshold}")
