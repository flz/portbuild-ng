import os

import portbuild.config as config
import portbuild.util as util


pbd = "/var/portbuild"

class Build:
  def __init__(self, arch, branch, buildid, config):
    self.arch = arch
    self.branch = branch
    self.buildid = buildid
    self.builddir = os.path.join(pbd, arch, branch, "builds", buildid)

    if not os.path.exists(os.path.join(pbd, arch)):
      error = "arch '%s' doesn't exist." % arch
      util.error(error)
      raise Exception(error)

    if not os.path.exists(os.path.join(pbd, arch, branch)):
      error = "branch '%s' doesn't exist." % branch
      util.error(error)
      raise Exception(error)

    if not os.path.exists(os.path.join(pbd, arch, branch, "builds", buildid)):
      error = "buildid '%s' doesn't exist." % buildid
      util.error(error)
      raise Exception(error)

  def setup(self):
    # Safe defaults for return values.
    success = False
    changed = True

    # Load the configuration files.
    self.config = config.Config(self.arch, self.branch)
    if not self.config.validate():
      return (False, changed)

    return (True, changed)

  def makestuff(self, args):
    """Spawns jobs that create metadata files"""
    if args.cdrom:
      self.makecdrom()

    if args.noindex:
      util.warn("ports tree changed but noindex option specified")
    else:
      self.makeindex()

    if args.norestr:
      util.warn("ports tree changed but norestr option specified")
    else:
      self.makerestr()

    if args.noduds:
      util.warn("ports tree changed but noduds option specified")
    else:
      self.makeduds()

  def makeindex(self):
    """Create INDEX file."""
    pass

  def makeduds(self):
    """Create INDEX file."""
    pass

  def makerestr(self):
    """Create INDEX file."""
    pass

  def makecdrom(self):
    """Create INDEX file."""
    pass
