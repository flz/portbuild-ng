import os
import tempfile

import ConfigParser

import portbuild.util as util


check_variables = [
  "pkg_sufx",
  "mailto",
]

class Config:
  def __init__(self, arch, branch):
    self._config = ConfigParser.SafeConfigParser()
    archpath = "/var/portbuild/%s/portbuild.conf" % (arch)
    branchpath = "/var/portbuild/%s/%s/portbuild.conf" % (arch, branch)

    # This is a bit hackish as the current configuration files don't use
    # sections and ConfigParser needs at least one...
    for cfg in [archpath, branchpath]:
      if os.path.exists(cfg):
        (ofd, cfgng) = tempfile.mkstemp(prefix="foo")
        o = os.fdopen(ofd, "w")
        o.write("[portbuild]\n")
        with open(cfg) as i:
          o.write(i.read())
        o.close()
        try:
          self._config.read(cfgng)
        except:
          pass
        os.unlink(cfgng)

  def validate(self):
    for i in check_variables:
      if not self._config.has_option("portbuild", i):
        util.error("Variable %s isn't set in portbuild.conf." % (i))
        return False
    return True

  def __getattr__(self, attr):
    if attr == "_config":
      return self.__dict__[attr]
    else:
      try:
        return self._config.get("portbuild", attr)
      except ConfigParser.NoOptionError:
        return None
