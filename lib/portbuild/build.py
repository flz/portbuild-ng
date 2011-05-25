import os
import time

import portbuild.config as config
import portbuild.tarball as tarball
import portbuild.util as util


pbd = "/var/portbuild"

class Build:
  def __init__(self, arch, branch, buildid, config):
    self.arch = arch
    self.branch = branch
    self.buildid = buildid
    self.builddir = os.path.join(pbd, arch, branch, "builds", buildid)
    self.start_time = time.time()

    if not os.path.exists(os.path.join(pbd, arch)):
      error = "Arch '%s' doesn't exist." % (arch)
      util.error(error)
      raise Exception(error)

    if not os.path.exists(os.path.join(pbd, arch, branch)):
      error = "Branch '%s' doesn't exist." % (branch)
      util.error(error)
      raise Exception(error)

    if not os.path.exists(os.path.join(pbd, arch, branch, "builds", buildid)):
      error = "Buildid '%s' doesn't exist." % (buildid)
      util.error(error)
      raise Exception(error)

  def finish(self):
    self.end_time = time.time()
    util.log("Build ended after %d seconds." % (self.end_time - self.start_time))

  def setup(self):
    success = False
    changed = False

    util.log("Setting up build...")

    # Load the configuration files.
    self.config = config.Config(self.arch, self.branch)
    if not self.config.validate():
      return (False, changed)

    # Deal with bindist.
    try:
      bt = tarball.BindistTarball(self.builddir)
    except:
      util.error("Couldn't find bindist.tbz.")
      return (False, changed)

    # Deal with ports.
    pt_orig = None
    try:
      pt_orig = tarball.PortsTarball(self.builddir)
    except:
      pass
    finally:
      path = tarball.PortsTarball.create(self.builddir)
      pt = tarball.PortsTarball(self.builddir, path)
      if not pt == pt_orig:
        changed = True
        pt.install()
        self.pt = pt
      else:
        util.log("Ports tarball unchanged.")
        pt.delete()

    # Deal with src.
    st_orig = None
    try:
      st_orig = tarball.SrcTarball(self.builddir)
    except:
      pass
    finally:
      path = tarball.SrcTarball.create(self.builddir)
      st = tarball.SrcTarball(self.builddir, path)
      if not st == st_orig:
        changed = True
        st.install()
        self.st = st
      else:
        util.log("Src tarball unchanged.")
        st.delete()

    return (True, changed)

  def makestuff(self, args):
    """Spawns jobs that create metadata files"""
    util.log("Generating metadata files...")

    if args.cdrom:
      self.makecdrom()

    if args.noindex:
      util.warn("Tarballs tree changed but noindex option specified.")
    else:
      self.makeindex()

    if args.norestr:
      util.warn("Tarballs changed but norestr option specified.")
    else:
      self.makerestr()

    if args.noduds:
      util.warn("Tarballs changed but noduds option specified.")
    else:
      self.makeduds()

  def makeindex(self):
    """Create INDEX file."""
    pass

  def makeduds(self):
    """Create duds file."""
    pass

  def makerestr(self):
    """Create restricted.sh file."""
    pass

  def makecdrom(self):
    """Create cdrom.sh file."""
    pass
