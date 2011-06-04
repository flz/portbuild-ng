import errno
import os
import subprocess

def mkdir_p(path):
  """Convenience routine to recursive create a hierarchy of directories."""
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else:
      raise

def debug(msg):
  """Simple warning routine."""
  print("D: " + str(msg))

def warn(msg):
  """Simple warning routine."""
  print("W: " + str(msg))

def error(msg):
  """Simple error routine."""
  print("E: " + str(msg))

def log(msg):
  """This isn't really useful."""
  print(str(msg))

def pipe_cmd(cmd, env=None, cwd=None):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=env, cwd=cwd)

def shell_cmd(cmd, env=None, cwd=None, quiet=False):
  p = pipe_cmd(cmd, env, cwd)
  if not quiet:
    for line in p.stdout.readlines():
      print line.rstrip()
  p.wait()
  return p

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
