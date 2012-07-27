import re
import io
import zipfile
import base64
import os.path

import requests
import yaml

BASE_URL = 'https://api.github.com/repos/{user}/{repo}/'
extension_index = {}
filename_index = {}


def get_repo(user, repo):
    url = BASE_URL.format(user=user, repo=repo)
    get_data(url)


def get_data(url):
    data = requests.get(url + 'zipball/master')
    data.raise_for_status()
    archive = zipfile.ZipFile(io.BytesIO(data.content))
    for name in archive.namelist():
        base = os.path.basename(name)
        if base:
            print(base, end=': ')
            lang = filename_index.get(base)
            if not lang:
                ext = os.path.splitext(base)[1]
                if ext:
                    lang = extension_index.get(ext)
            print(lang)


def get_important_repos():
    important_repos = requests.get('https://github.com/repositories')
    important_repos.raise_for_status()
    url_matches = re.finditer(r'<a href="/(\w*)/([^/]*)">\2</a>\n',
                            important_repos.text)
    results = ((match.group(1), match.group(2)) for match in url_matches)
    repos = ((user, repo) for ((user, repo), _) in zip(results, results))
    return repos


def init_linguist():
    '''get GitHub's programming language identification database'''
    r = requests.get(BASE_URL.format(user='github', repo='linguist') +
                     'contents/lib/linguist/languages.yml')
    r.raise_for_status()
    content = base64.b64decode(r.json['content'].encode('utf-8'))
    linguist = yaml.load(content)
    build_index(linguist)


def build_index(linguist):
    '''create two reverse indexes for extensions and filenames to language'''
    global extension_index
    global filename_index
    for lang, data in linguist.items():
        exts = {data.get('primary_extension')}
        exts = exts.union(data.get('extensions', {}))
        for ext in exts.union(data.get('overrides', {})):
            extension_index[ext] = lang
        for name in data.get('filenames', []):
            filename_index[name] = lang


def main():
    init_linguist()
    repos = get_important_repos()
    test = list(repos)[0]
    get_repo(*test)

if __name__ == '__main__':
    main()
