import os
import tempfile

import ConfigParser

import portbuild.util as util

pbd = "/var/portbuild"

check_variables = [
  "pkg_sufx",
  "mailto",
]

class ConfigException(Exception):
  pass

class InvalidConfig(ConfigException):
  pass

class Config:
  def __init__(self, arch, branch):
    self._config = ConfigParser.SafeConfigParser()
    archpath = os.path.join(pbd, arch, "portbuild.conf")
    branchpath = os.path.join(pbd, arch, branch, "portbuild.conf")

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

    for i in check_variables:
      if not self._config.has_option("portbuild", i):
        error = "Variable '{0}' isn't set in portbuild.conf.".format(i)
        util.error(error)
        raise InvalidConfig(error)

  def __getattr__(self, attr):
    if attr == "_config":
      return self.__dict__[attr]
    else:
      try:
        return self._config.get("portbuild", attr)
      except ConfigParser.NoOptionError:
        return None

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
