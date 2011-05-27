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

def warn(msg):
  """Simple warning routine."""
  print("W: %s" % (msg))

def error(msg):
  """Simple error routine."""
  print("E: %s" % (msg))

def log(msg):
  """This isn't really useful."""
  print(msg)

def pipe_cmd(cmd, env=None, cwd=None):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=env)

def shell_cmd(cmd, env=None, cwd=None, quiet=False):
  cmd = pipe_cmd(cmd, env, cwd)
  if quiet:
    cmd.wait()
    return cmd
  else:
    for line in cmd.stdout.readlines():
      print line.rstrip()

# vim: tabstop=2 shiftwidth=2 expandtab
