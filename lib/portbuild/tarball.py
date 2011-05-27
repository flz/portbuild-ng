import os
import tempfile

import portbuild.util as util

pbd = "/var/portbuild"


class Tarball:
  def __init__(self, builddir, component, path):
    """Create a tarball object."""
    self.component = component
    self.path = path
    self.realpath = path
    self.builddir = builddir

    if not os.path.exists(path):
      raise IOError("%s doesn't exist" % (path))

    cmd = util.pipe_cmd("/sbin/sha256 -q %s" % (path))
    self.checksum = cmd.stdout.readline().strip()

  def __eq__(self, other):
    """Check if two tarball objects are the same."""
    if other == None:
      return False
    else:
      return self.checksum == other.checksum

  def promote(self, dest=None):
    """Put the tarball where it should be."""
    # dest might be used as a compatibility shim.
    if dest == None:
      dest = os.path.join(self.builddir, "%s.tbz" % (self.component))

    cachedir = os.path.join(pbd, "tarballs")
    if os.path.isdir(cachedir):
      self.realpath = os.path.join(cachedir, "%s-%s.tbz" % (self.component, self.checksum[0:16]))
      os.rename(self.path, self.realpath)
      self.path = dest
      if os.path.lexists(self.path):
        os.unlink(self.path)
      os.symlink(self.realpath, self.path)
      util.log("Tarball cached as %s" % (self.realpath))
    else:
      os.rename(self.path, dest)
      self.path = dest
      self.realpath = dest

  def delete(self):
    """Delete underlying tarball file."""
    # This is meant to be called instead of promote().
    os.unlink(self.path)

  @staticmethod
  def create(builddir, component):
    """Create a new tarball."""
    cachedir = os.path.join(pbd, "tarballs")
    if os.path.isdir(cachedir):
      destdir = cachedir
    else:
      destdir = builddir
    prefix = "%s-" % (component)
    (f, tmp) = tempfile.mkstemp(dir=destdir, prefix=prefix, suffix=".tbz")
    util.log("Creating %s tarball..." % (component))
    cmd = "/usr/bin/tar -C %s -cjf %s %s" % (builddir, tmp, component)
    try:
      util.shell_cmd(cmd)
    except KeyboardInterrupt:
      print "Cleaning up temporary tarball..."
      os.unlink(tmp)
      raise
    else:
      return Tarball(builddir, component, tmp)

class PortsTarball(Tarball):
  def __init__(self, builddir, path=None):
    if path == None:
      path = os.path.join(builddir, "ports.tbz")
    Tarball.__init__(self, builddir, "ports", path)

  @staticmethod
  def create(base):
    return Tarball.create(base, "ports")

class SrcTarball(Tarball):
  def __init__(self, builddir, path=None):
    if path == None:
      path = os.path.join(builddir, "src.tbz")
    Tarball.__init__(self, builddir, "src", path)

  @staticmethod
  def create(base):
    return Tarball.create(base, "src")

class BindistTarball(Tarball):
  def __init__(self, builddir):
    path = os.path.join(builddir, "bindist.tbz")
    Tarball.__init__(self, builddir, "bindist", path)

# vim: tabstop=2 shiftwidth=2 expandtab
