import os
import time
import git

import subprocess

import shutil

POLLING_RATE = 30 # seconds

GIT_DIRECTORIES = []

REACT_REPOSITORY = ""

PUBLIC_DIRECTORY = ""

def empty():
    for filename in os.listdir(PUBLIC_DIRECTORY):
        filepath = PUBLIC_DIRECTORY + '/' + filename
        if os.path.isdir(filepath):
            shutil.rmtree(filepath, ignore_errors=True)
        else:
            os.remove(filepath)

def replace_loading():
    empty()
    for filename in os.listdir("replace"):
        shutil.copy("replace/" + filename, PUBLIC_DIRECTORY)
    
def publish():
    empty()
    if os.path.isdir(REACT_REPOSITORY + '/build'):
        for item in os.listdir(REACT_REPOSITORY + '/build/'):
            item_path = REACT_REPOSITORY + '/build/' + item
            if os.path.isdir(item_path):
                os.mkdir(PUBLIC_DIRECTORY + '/' + item)
                shutil.copytree(item_path, PUBLIC_DIRECTORY + '/' + item, dirs_exist_ok=True)
            else:
                shutil.copy(item_path, PUBLIC_DIRECTORY + '/')


react_repo = git.Repo(REACT_REPOSITORY)
while True:
    print("checking for update platform...")

    current_hash = react_repo.head.object.hexsha
    o = react_repo.remotes.origin
    o.fetch()
    changed = o.refs['main'].object.hexsha != current_hash
    if changed:
        print("updates found for mindclick")
        replace_loading()
        react_repo.remotes.origin.pull()
        subprocess.call('npm install --save', shell=True, cwd=REACT_REPOSITORY)
        subprocess.call("npm run build", cwd=REACT_REPOSITORY, shell=True)
        publish()
    else:
        print("no updates for mindclick")

    for repo_dir in GIT_DIRECTORIES:
        repo = git.Repo(repo_dir)
        current_hash = repo.head.object.hexsha
        o = repo.remotes.origin
        o.fetch()
        try:
            changed = o.refs['main'].object.hexsha != current_hash
        except:
            changed = o.refs['master'].object.hexsha != current_hash
        if changed:
            print("updates found for " + repo_dir)
            replace_loading()
            repo.remotes.origin.pull()
            subprocess.call('npm install --save', shell=True, cwd=repo_dir)
            subprocess.call("pm2 restart all", shell=True)
            publish()
        else:
            print("no updates for " + repo_dir)

    time.sleep(POLLING_RATE)