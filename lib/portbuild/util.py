import errno
import os

def mkdir_p(path):
  """Convenience routine to recursive create a hierarchy of directories."""
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else:
      raise

def warn(msg):
  """Simple warning routine."""
  print("W: %s" % (msg))

def error(msg):
  """Simple error routine."""
  print("E: %s" % (msg))
