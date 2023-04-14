#!/usr/bin/python3
import re
import requests
import tarfile
import urllib
import os

base_url = "https://ftp.fau.de/pub/OpenBSD/LibreSSL/"

req = requests.get(base_url)

python_dists = []

for line in req.iter_lines():
    search = re.search(r'<a href=\"(.*)-([0-9]*)\.([0-9]*)\.([0-9]*)\.tar\.gz\">', line.decode())
    if search != None:
        print("found: " + search.group(1) + " - version " + search.group(2) + "." + search.group(3) + "." + search.group(4))
        python_dists.append([search.group(0), search.group(1), search.group(2), search.group(3), search.group(4)])

for dist in python_dists:
    command = "git tag -l v" +dist[2]+'.'+dist[3]+'.'+dist[4]
    if(os.popen(command).read() != ""):
       continue
    url = base_url + dist[1] + '-'+dist[2]+'.'+dist[3]+'.'+dist[4]+'.tar.gz'
    print(url)
    tmpFile = urllib.request.urlretrieve(url, filename=None)
    base_name = os.path.basename(url)
    file_name, file_extension = os.path.splitext(base_name)
    print(tmpFile[0])
    tar = tarfile.open(tmpFile[0], mode='r')
    tar.extractall("../tmp/")
    print(file_name)
    tmp, tmp_extension = os.path.splitext(file_name)
    print(tmp)
    command = "git checkout -f master"
    os.popen(command).read()
    command = "bash -c 'rm -rf *; echo done'" 
    if(os.popen(command).read() != "done\n"):
       continue
    command = "mv ../tmp/" + tmp +"/* ."
    if(os.popen(command).read() != ""):
       continue
    command = "git add *"
    if(os.popen(command).read() != ""):
       continue
    command = "git commit -a -m 'import v"+ dist[2]+'.'+dist[3]+'.'+dist[4] + "'"
    os.popen(command).read()
    command = "git tag v"+ dist[2]+'.'+dist[3]+'.'+dist[4]
    if(os.popen(command).read() != ""):
       continue

