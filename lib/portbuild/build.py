import portbuild.config as config
import portbuild.util as util

class Build:
  def __init__(self, arch, branch, buildid, config):
    self.arch = arch
    self.branch = branch
    self.buildid = buildid
    self.builddir = "/var/portbuild/%s/%s/builds/%s" % (arch, branch, buildid)

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
