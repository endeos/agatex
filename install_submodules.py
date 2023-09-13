# Script to install submodules listed in file install_submodules.txt

import os

ODOO_VERSION_BRANCH = 16.0

lines = []
with open("install_submodules.txt", "r") as f:
    lines = [line.strip() for line in f.readlines()]

def install_submodule(url, module):
    res = os.system(f"git submodule add --force --branch {ODOO_VERSION_BRANCH} {url} {module}")
    return res

for repo_url in lines:
    url = repo_url
    module = url[19:]
    
    if not module.startswith("OCA/"):
        print(f"Loop break. Check module URLS, this is different: {repo_url}")
        break

    install_submodule(url, module)