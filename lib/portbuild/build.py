import os
import re
import time

import portbuild.config as config
import portbuild.tarball as tarball
import portbuild.torrent as torrent
import portbuild.util as util

pbc = "/var/portbuild"
pbd = "/var/portbuild"

class BuildException(Exception):
  pass

class BuildDoesntExist(BuildException):
  pass

class BuildInvalidConfig(BuildException):
  pass

class BuildMissingComponent(BuildException):
  pass

class BuildMissingMetadata(BuildException):
  pass

class Build:
  def __init__(self, arch, branch, buildid):
    self.start_time = time.time()
    self.arch = arch
    self.branch = branch
    self.buildid = buildid
    self.builddir = os.path.realpath(os.path.join(pbd, arch, branch, "builds", buildid))
    self.tarballs = []

    # A few sanity checks.
    error = None
    if not os.path.exists(os.path.join(pbd, arch)):
      error = "Arch '%s' doesn't exist." % (arch)
    elif not os.path.exists(os.path.join(pbd, arch, branch)):
      error = "Branch '%s' doesn't exist." % (branch)
    elif not os.path.exists(self.builddir):
      error = "Buildid '%s' doesn't exist." % (buildid)

    if error:
      raise BuildDoesntExist(error)

    self.subset = None
    self.subsetfile = None
    self.portsdir = os.path.join(self.builddir, "ports")
    self.srcdir = os.path.join(self.builddir, "src")
    self.indexfile = os.path.join(self.builddir, "INDEX-%s" % (self.branch[0]))
    self.dudsfile = os.path.join(self.builddir, "duds")
    self.restrfile = os.path.join(self.builddir, "restricted.sh")

  def buildenv(self):

    # These are from scripts/buildenv
    self.buildenv = { }
    self.buildenv["PORTSDIR"] = self.portsdir
    self.buildenv["SRC_BASE"] = self.srcdir
    self.buildenv["PORT_DBDIR"] = "/nonexistent"
    self.buildenv["DISTDIR"] = os.path.join(self.builddir, "distfiles")
    self.buildenv["PACKAGES"] = os.path.join(self.builddir, "packages")
    self.buildenv["INDEXFILE"] = os.path.basename(self.indexfile)
    self.buildenv["ARCH"] = self.arch
    self.buildenv["MACHINE_ARCH"] = self.arch
    self.buildenv["BATCH"] = "yes"
    self.buildenv["PACKAGE_BUILDING"] = "1"

    # And the tricky ones...
    with open("%s/sys/sys/param.h" % (self.srcdir)) as f:
      ver = [i.split()[2] for i in f.readlines() \
             if re.match("^#define __FreeBSD_version", i)]
      self.buildenv["OSVERSION"] = ver[0]

    with open("%s/sys/conf/newvers.sh" % (self.srcdir)) as f:
      lines = f.readlines()
      rev = [i.split('"')[1] for i in lines if re.match("^REVISION", i)]
      branch = [i.split('"')[1] for i in lines if re.match("^BRANCH", i)]
      self.buildenv["OSREL"] = rev[0]
      self.buildenv["BRANCH"] = branch[0]

  def finish(self):
    self.seed_stop()
    self.end_time = time.time()
    util.log("Build ended after %d seconds." %
             (self.end_time - self.start_time))

  def set_subset(self, target):
    # Not happy with that, but I need it for testing.
    self.subsetfile = target
    with open(target) as f:
      self.subset = [line.rstrip() for line in f.readlines()]

  def setup(self):
    changed = False

    util.log("Setting up build...")

    self.buildenv()

    # Load the configuration files.
    try:
      self.config = config.Config(self.arch, self.branch)
    except config.InvalidConfig as e:
      raise BuildInvalidConfig(e)

    try:
      self.__setup_bindist()
      changed |= self.__setup_ports()
      changed |= self.__setup_src()
    except BuildMissingComponent:
      raise

    return changed

  def __setup_bindist(self):
    """Create bindist Tarball object."""
    try:
      bt = tarball.BindistTarball(self.builddir)
      bt.promote()
      self.tarballs.append(bt)

    except IOError as e:
      raise BuildMissingComponent(e)

  def __setup_ports(self):
    """Create new ports tarball and Tarball object."""
    changed = False
    pt_orig = None
    try:
      pt_orig = tarball.PortsTarball(self.builddir)
    except:
      pass
    try:
      pt = tarball.PortsTarball.create(self.builddir)
    except KeyboardInterrupt:
      error = "Ports tarball creation was interrupted"
      raise BuildMissingComponent(error)
    if not pt == pt_orig:
      changed = True
      pt.promote()
      self.tarballs.append(pt)
    else:
      util.log("Ports tarball unchanged.")
      self.tarballs.append(pt_orig)
      pt.delete()
    return changed

  def __setup_src(self):
    """Create new src tarball and Tarball object."""
    changed = False
    st_orig = None
    try:
      st_orig = tarball.SrcTarball(self.builddir)
    except:
      pass
    try:
      st = tarball.SrcTarball.create(self.builddir)
    except KeyboardInterrupt:
      error = "Src tarball creation was interrupted"
      raise BuildMissingComponent(error)
    if not st == st_orig:
      changed = True
      st.promote()
      self.tarballs.append(st)
    else:
      util.log("Src tarball unchanged.")
      self.tarballs.append(st_orig)
      st.delete()
    return changed

  def metagen(self, changed, args):
    """Create metadata files"""

    buildindex = True
    if os.path.exists(self.indexfile):
      if not changed:
        buildindex = False
      elif args.noindex:
        util.warn("Tarballs tree changed but noindex option specified.")
        buildindex = False
    else:
      if args.noindex:
        util.error("No index found but noindex option specified.")
        return False
    if buildindex:
      self.makeindex()

    buildduds = True
    if os.path.exists(self.dudsfile):
      if not changed:
        buildduds = False
      elif args.noduds:
        util.warn("Tarballs tree changed but noduds option specified.")
        buildduds = False
    else:
      if args.noduds:
        util.error("No duds found but noduds option specified.")
        return False
    if buildduds:
      self.makeduds()

    buildrestr = True
    if os.path.exists(self.restrfile):
      if not changed:
        buildrestr = False
      elif args.norestr:
        util.warn("Tarballs tree changed but norestr option specified.")
        buildrestr = False
    else:
      if args.norestr:
        util.error("No restr found but norestr option specified.")
        return False
    if buildrestr:
      self.makerestr()

    if args.cdrom:
      self.makecdrom()

  def makeindex(self):
    """Create INDEX file."""
    # Set a few environment variables. Add whatever is in buildenv and then
    # makeindex specific variables.
    environ = { }
    environ.update(os.environ)
    environ.update(self.buildenv)
    environ["INDEXDIR"] = self.builddir
    environ["INDEX_PRISTINE"] = "1"
    environ["INDEX_QUIET"] = "1"
    environ["INDEX_JOBS"] = "6"
    environ["LOCALBASE"] = "/nonexistentlocal"

    error = None
    cmd = "%s/scripts/makeindex %s %s %s %s" % \
      (pbc, self.arch, self.branch, self.buildid, \
       self.subsetfile if self.subsetfile else "")

    util.log("Creating INDEX file...")
    try:
      f = util.pipe_cmd(cmd, env=environ, cwd=self.portsdir)
      success = "^Generating %s - please wait.. Done.$" % \
        (os.path.basename(self.indexfile))
      for i in f.stdout.readlines():
        if re.match(success, i.rstrip()):
          break
        else:
          print i.rstrip()
      f.wait() 
    except KeyboardInterrupt:
      pass

    if f.returncode != 0:
      error = "Failed to build INDEX file."

    if error:
      raise BuildMissingMetadata(error)

  def makeduds(self):
    """Create duds file."""
    environ = { }
    environ.update(os.environ)
    environ.update(self.buildenv)

    environ["ECHO_MSG"] = "true"

    environ["__MAKE_SHELL"] = "/rescue/sh"
    environ["LOCALBASE"] = "/nonexistentlocal"
    environ["LINUXBASE"] = "/nonexistentlinux"
    environ["PKG_DBDIR"] = "/nonexistentpkg"
    environ["PORT_DBDIR"] = "/nonexistentport"

    error = None
    cmd = "%s/scripts/makeduds %s %s %s %s" % \
      (pbc, self.arch, self.branch, self.buildid, \
       self.subsetfile if self.subsetfile else "")

    util.log("Creating duds file...")
    try:
      f = util.shell_cmd(cmd, env=environ, cwd=self.portsdir)
      if f.returncode != 0:
        error = "Failed to build duds file."
    except KeyboardInterrupt:
      error = "Failed to build duds file."

    if error:
      raise BuildMissingMetadata(error)

  def makerestr(self):
    """Create restricted.sh file."""
    environ = { }
    environ.update(os.environ)
    environ.update(self.buildenv)

    environ["__MAKE_SHELL"] = "/rescue/sh"
    environ["LOCALBASE"] = "/nonexistentlocal"
    environ["LINUXBASE"] = "/nonexistentlinux"
    environ["PKG_DBDIR"] = "/nonexistentpkg"
    environ["PORT_DBDIR"] = "/nonexistentport"

    error = None
    cmd = "%s/scripts/makerestr %s %s %s %s" % \
      (pbc, self.arch, self.branch, self.buildid, \
       self.subsetfile if self.subsetfile else "")

    util.log("Creating restricted.sh file...")
    try:
      f = util.shell_cmd(cmd, cwd=self.portsdir)
      if f.returncode != 0:
        error = "Failed to build restricted.sh file."
    except KeyboardInterrupt:
      error = "Failed to build restricted.sh file."

    if error:
      raise BuildMissingMetadata(error)

  def makecdrom(self):
    """Create cdrom.sh file."""
    pass

  def seed_start(self):
    """Start seeding the build tarballs."""
    self.ts = torrent.TorrentSession()
    util.log("Start seeding...")
    for t in self.tarballs:
      t.torrent = torrent.Torrent.create(t.realpath)
      t.torrent.dump()
      self.ts.add(t.torrent)

  def seed_stop(self):
    """Stop seeding the build tarballs."""
    util.log("Stop seeding...")
    self.ts.terminate()

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
