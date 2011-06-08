# Artificially bump priority for these packages.
QMANAGER_PRIORITY_PACKAGES = ""

# Port status codes
PENDING = 1 # Yet to build
PHASE2 = 2  # Failed once

class Package:
  def __init__(self, name, path, prefix, comment, descr, maintainer,
               cats, www):

    __slots__ = ["name", "path", "prefix", "comment", "descr",
                 "maintainer", "www", "bdep", "rdep", "edep", "pdep",
                 "fdep", "alldep", "parents",  "depth", "categories"]

    self.name = name
    self.path = path
    self.prefix = prefix
    self.comment = comment
    self.descr = descr
    self.maintainer = maintainer
    self.categories = cats
    self.www = www

    # Populated later
    self.fdep = []
    self.edep = []
    self.bdep = []
    self.rdep = []
    self.pdep = []
    self.alldep = []
    self.parents = []

    self.status = PENDING
    self.attempts = 0

    # Whether the package build has completed and is hanging around
    # to resolve dependencies for others XXX use status
    self.done = False

    # Depth is the maximum length of the dependency chain of this port
    self.depth = None


  def set_depth_recursive(self):
    """Recursively populate the depth tree up from a given package
    through dependencies, assuming empty values on entries not yet
    visited."""
    if self.depth is None:
      if len(self.parents) > 0:
        max = 0
        for i in self.parents:
          w = i.set_depth_recursive()
          if w > max:
            max = w
            self.depth = max + 1
      else:
        self.depth = 1
        for port in QMANAGER_PRIORITY_PACKAGES:
          if self.name.startswith(port):
          # Artificial boost to try and get it building earlier
            self.depth = 100
    return self.depth

  def remove(self):
    """ Clean ourselves up but don't touch references in other objects;
they still need to know about us as dependencies etc """

    self.fdep = None
    self.edep = None
    self.pdep = None
    self.bdep = None
    self.rdep = None
    self.alldep = None
    self.parents = None

  def destroy(self):
    """ Remove a package and all references to it """
    for pkg in self.alldep:
      if pkg.parents is not None:
        # Already removed but not destroyed
        try:
          pkg.parents.remove(self)
        except ValueError:
          continue
        
    # Remove references to current package in all dependents.
    for pkg in self.parents:
      try:
        pkg.fdep.remove(self)
      except ValueError:
        pass
      try:
        pkg.edep.remove(self)
      except ValueError:
        pass
      try:
        pkg.pdep.remove(self)
      except ValueError:
        pass
      try:
        pkg.bdep.remove(self)
      except ValueError:
        pass
      try:
        pkg.rdep.remove(self)
      except ValueError:
        pass
      pkg.alldep.remove(self)

    self.remove()

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
