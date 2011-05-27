#! /usr/bin/env python2.7

import argparse
import sys

import portbuild.build as build
import portbuild.util as util

options = {
  "cdrom":		"prepare a build for distribution on cdrom",
#  "continue":		"restart an interrupted build, skipping failed ports",
#  "fetchoriginal":	"fetch from original MASTER_SITES",
#  "finish":		"post-process a completed build",
#  "incremental":	"start incremental build",
#  "keep":		"don't recycle this build",
#  "nobuild":		"don't build any packages",
#  "nochecksubdirs":	"don't check SUBDIRS for missing ports",
#  "nocleanup":		"don't clean up and deactivate the build upon completion",
#  "nodistfiles":	"don't collect distfiles",
  "noduds":		"don't build the duds file",
  "noindex":		"don't build the INDEX file",
#  "nofinish":		"don't post-process upon build completion",
#  "noplistcheck":	"don't check the plist during the build",
  "norestr":		"don't build the restricted.sh file",
#  "ports":		"update the ports tree snapshot",
#  "portsvcs":		"update the ports tree from the repository",
#  "restart":		"restart an interrupted build, rebuilding failed ports",
#  "src":		"update the src tree snapshot",
#  "srcvcs":		"update the src tree from the repository",
#  "trybroken":		"try to build BROKEN ports",
}

parser = argparse.ArgumentParser(description='Build some packages.')

# Boolean options
for name, descr in options.iteritems():
  parser.add_argument("-%s" % (name), action="store_true", help=descr)

# Other options
parser.add_argument("-target", metavar="file", help="Subset of the ports tree to build")

# Mandatory arguments
parser.add_argument("arch")
parser.add_argument("branch")
parser.add_argument("buildid", nargs="?", default="latest")

args = parser.parse_args()

arch = args.arch
branch = args.branch
buildid = args.buildid

try:
  build = build.Build(arch, branch, buildid)
except Exception, e:
  print e
  sys.exit(1)

if args.target:
  build.set_subset(args.target)

(success, changed) = build.setup()

if not success:
  util.error("Failed to setup build. Exiting.")
  sys.exit(1)

build.metagen(changed, args)

build.finish()

# vim: tabstop=2 shiftwidth=2 expandtab
