import itertools

import portbuild.package as package


class Index:
  def __init__(self, indexfile):
    self.indexfile = indexfile
    self.packages = {}

  def parse(self, targets = None):
    with open(self.indexfile) as f:
      index = f.readlines()

    lines = []
    for i in index:
      (name, path, prefix, comment, descr, maintainer, categories, bdep,
       rdep, www, edep, pdep, fdep) = i.rstrip().split("|")

      if targets is None or name in targets:
        self.packages[name] = package.Package(name, path, "", "", "", "", categories, "")
        lines.append((name, bdep, rdep, edep, pdep, fdep))

    for (name, bdep, rdep, edep, pdep, fdep) in lines:
      self.setdeps(self.packages[name], bdep, rdep, edep, pdep, fdep)

  def setdeps(self, package, bdep, rdep, edep, pdep, fdep):
    package.fdep = [self.packages[p] for p in fdep.split()]
    package.edep = [self.packages[p] for p in edep.split()]
    package.pdep = [self.packages[p] for p in pdep.split()]
    package.bdep = [self.packages[p] for p in bdep.split()]
    package.rdep = [self.packages[p] for p in rdep.split()]

    package.alldep = list(set(itertools.chain(package.fdep, package.edep, package.pdep,
                                 package.bdep, package.rdep)))

    for p in package.alldep:
      p.parents.append(package)

  def destroy_recursive(self, package):
    """ Remove a port and everything that depends on it """
    parents = set([package])

    while len(parents) > 0:
      pkg = parents.pop()
      assert pkg.depth is not None
      parents.update(pkg.parents)
      pkg.destroy()
      del self.packages[pkg.name]

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
