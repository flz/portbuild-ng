import os
import time

import portbuild.dispatcher as dispatcher
import portbuild.index as index


class Scheduler:
  def __init__(self, build):
    self.build = build
    self.dispatcher = dispatcher.Dispatcher(build, self.on_success, self.on_failure)

  def prepare(self):
    self.index = index.Index(self.build.indexfile)
    self.index.parse()
    # For now we'll build everything.
    self.targets = self.gettargets()
    self.depthindex(self.targets)

    # Remove duds from the ports list.
    with open(os.path.join(self.build.builddir, "duds")) as f:
      for line in f.readlines():
        try:
          dud = self.index.packages[line.rstrip()]
          self.index.destroy_recursive(dud)
        except KeyError:
          pass

  def gettargets(self, targets=None):
    """Returns array of all ports that will be built including dependencies """

    pkg_sufx = self.build.config.pkg_sufx

    plist = set()
    if not targets:
        targets = ["all"]
    for i in targets:
        if i == "all":
            return self.index.packages.itervalues()
        elif i.rstrip(pkg_sufx) in self.index.packages:
            plist.update([self.index.packages[i.rstrip(pkg_sufx)].name])
        else:
            raise KeyError, i

    # Compute transitive closure of all dependencies
    pleft=plist.copy()
    while len(pleft) > 0:
      pkg = pleft.pop()
      new = [p.name for p in self.index.packages[pkg].alldep]
      plist.update(new)
      pleft.update(new)

    for p in set(self.index.packages.keys()).difference(plist):
      self.index.packages[p].destroy()

    return [self.index.packages[p] for p in plist]

  def start(self):
    self.dispatcher.start()

    # XXX can do this while parsing index if we prune targets/duds first
    for pkg in self.index.packages.itervalues():
      if len(pkg.alldep) == 0:
        self.dispatcher.dispatch(pkg)

  def stop(self):
    self.dispatcher.stop()

  def depthindex(self, targets):
    """ Initial population of depth tree """
    for p in targets:
      p.set_depth_recursive()

  def on_success(self, name):
    """Callback, used when a build succeeded."""
    p = self.index.packages[name]
    parents = p.parents[:]
    p.done = True
    p.remove()
    del self.index.packages[name]

    newleaves = [p for p in parents if all(c.done for c in p.alldep)]
    for p in newleaves:
      self.dispatcher.dispatch(p)

  def on_failure(self, name):
    """Callback, used when a build failed."""
    self.destroy_recursive(self.index.packages[name])

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
