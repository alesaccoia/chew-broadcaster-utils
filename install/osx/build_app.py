#!/usr/bin/env python3.3
 
candidate_paths = "bin obs-plugins".split()
candidate_suffixes = "dylib so".split()
 
 
plist_path = "../cmake/osxbundle/Info.plist"
icon_path = "../cmake/osxbundle/obs.icns"
run_path = "../cmake/osxbundle/obslaunch.sh"
 
#not copied
blacklist = """/usr /System""".split()
 
#copied
whitelist = """/usr/local""".split()
 
#
#
#
 
 
from sys import argv
from glob import glob
from subprocess import check_output, call
from collections import namedtuple
from shutil import copy, copytree, rmtree
from os import makedirs, rename
import plistlib

import argparse
parser = argparse.ArgumentParser(description='obs-studio package util')
parser.add_argument('-d', '--base-dir', dest='dir', default='rundir/RelWithDebInfo')
parser.add_argument('-b', '--build-number', dest='build_number', default='0')
args = parser.parse_args()

def cmd(cmd):
    import subprocess
    import shlex
    return subprocess.check_output(shlex.split(cmd)).rstrip('\r\n')

LibTarget = namedtuple("LibTarget", ("path", "external", "copy_as"))
 
inspect = list()
 
inspected = set()
 
build_path = args.dir
build_path = build_path.replace("\\ ", " ")
 
def add(name, external=False, copy_as=None):
	if external and copy_as is None:
		copy_as = name.split("/")[-1]
	if name[0] != "/":
		name = build_path+"/"+name
	t = LibTarget(name, external, copy_as)
	if t in inspected:
		return
	inspect.append(t)
	inspected.add(t)
 
add("bin/obs")
 
for i in candidate_paths:
	for j in candidate_suffixes:
		print(build_path+"/"+i+"/*."+j)
		for k in glob(build_path+"/"+i+"/*."+j):
			rel_path = k[len(build_path)+1:]
			print(repr(k), repr(rel_path))
			add(rel_path)
 
def add_plugins(path, replace):
	for img in glob(path.replace(
		"lib/QtCore.framework/Versions/5/QtCore",
		"plugins/%s/*"%replace).replace(
			"Library/Frameworks/QtCore.framework/Versions/5/QtCore",
			"share/qt5/plugins/%s/*"%replace)):
		if "_debug" in img:
			continue
		add(img, True, img.split("plugins/")[-1])
 
 
while inspect:
	target = inspect.pop()
	print("inspecting", repr(target))
	path = target.path
	if path[0] == "@":
		continue
	out = check_output("otool -L '%s'"%path, shell=True,
			universal_newlines=True)
 
	if "QtCore" in path:
		plugin = path.replace("lib/QtCore.framework/Versions/5/QtCore",
				"plugins/platforms/libqcocoa.dylib")
		plugin = path.replace("Library/Frameworks/QtCore.framework/Versions/5/QtCore",
				"share/qt5/plugins/platforms/libqcocoa.dylib")
		add(plugin, "True", "platforms/libqcocoa.dylib")
		add_plugins(path, "imageformats")
		add_plugins(path, "accessible")
 
 
	for line in out.split("\n")[1:]:
		new = line.strip().split(" (")[0]
		if not new or new[0] == "@" or new.endswith(path.split("/")[-1]):
			continue
		whitelisted = False
		for i in whitelist:
			if new.startswith(i):
				whitelisted = True
		if not whitelisted:
			blacklisted = False
			for i in blacklist:
				if new.startswith(i):
					blacklisted = True
					break
			if blacklisted:
				continue
		add(new, True)
 
changes = list()
for path, external, copy_as in inspected:
	if not external:
		continue #built with install_rpath hopefully
	changes.append("-change '%s' '@rpath/%s'"%(path, copy_as))
changes = " ".join(changes)
 

info = plistlib.readPlist(plist_path)



latest_tag = cmd('git describe --tags --abbrev=0')
log = cmd('git log --pretty=oneline {0}...HEAD'.format(latest_tag))

# set version
info["CFBundleVersion"] = "%s.%s"%(cmd("git rev-list HEAD --count"), args.build_number)
info["CFBundleShortVersionString"] = "%s.%s"%(latest_tag, len(log.splitlines()))
 
app_name = info["CFBundleName"]+".app"
icon_file = "tmp/Contents/Resources/%s"%info["CFBundleIconFile"]
 
copytree(build_path, "tmp/Contents/Resources/", symlinks=True)
copy(icon_path, icon_file)
plistlib.writePlist(info, "tmp/Contents/Info.plist")
makedirs("tmp/Contents/MacOS")
copy(run_path, "tmp/Contents/MacOS/%s"%info["CFBundleExecutable"])

prefix = "tmp/Contents/Resources/"
 
for path, external, copy_as in inspected:
	id_ = ""
	filename = path
	rpath = ""
	if external:
		id_ = "-id '@rpath/%s'"%copy_as
		filename = prefix + "bin/" +copy_as
		rpath = "-add_rpath @loader_path/ -add_rpath @executable_path/"
		if "/" in copy_as:
			try:
				dirs = copy_as.rsplit("/", 1)[0]
				makedirs(prefix + "bin/" + dirs)
			except:
				pass
		copy(path, filename)
	else:
		filename = path[len(build_path)+1:]
		id_ = "-id '@rpath/../%s'"%filename
		filename = prefix + filename
 
	cmd = "install_name_tool %s %s %s '%s'"%(changes, id_, rpath, filename)
	#print(repr(cmd))
	call(cmd, shell=True)
 
try:
	rename("tmp", app_name)
except:
	print("App already exists")
	rmtree("tmp")