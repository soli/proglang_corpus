import re
import io
import zipfile
import base64
import os
import os.path
import collections
import itertools
import tempfile

import requests
import yaml

BASE_URL = 'https://api.github.com/repos/{user}/{repo}/'
extension_index = {}
filename_index = {}


def process_repo(user, repo, corpus_dir):
    '''append files of user/repo to language files in corpus_dir'''
    print('processing repo: {user}/{repo}'.format(user=user, repo=repo))
    url = BASE_URL.format(user=user, repo=repo)
    data = get_data(url)
    write_data(data, corpus_dir)


def get_data(url):
    '''return dictionary lang -> lines for the github project given as url'''
    lang_data = collections.defaultdict(list)

    data = requests.get(url + 'zipball/master')
    try:
        data.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('got ' + str(e) + ' when accessing ' + url)
    else:
        archive = zipfile.ZipFile(io.BytesIO(data.content))
        update_lang_data(lang_data, archive)

    return lang_data


def update_lang_data(lang_data, archive):
    '''for each recognized file in archive, add its lines to lang_data'''
    for name in archive.namelist():
        base = os.path.basename(name)
        if base:
            lang = identify_lang(base)
            if lang:
                with archive.open(name) as f:
                    lang_data[lang].extend(f.readlines())


def identify_lang(filename):
    lang = filename_index.get(filename)
    if not lang:
        ext = os.path.splitext(filename)[1]
        if ext:
            lang = extension_index.get(ext)
    return lang


def write_data(lang_data, corpus_dir):
    '''append lines stored in lang_data to files in corpus_dir
    those files are named by language'''
    for lang, lines in lang_data.items():
        with open(os.path.join(corpus_dir, lang), 'a') as f:
            f.writelines([l.decode(errors='ignore') for l in lines])


def get_important_repos(num=25):
    '''return the repositories listed on github "important" page
    as a generator of pairs (user, repo)'''
    important_repos = requests.get('https://github.com/repositories')
    important_repos.raise_for_status()
    url_matches = re.finditer(r'<a href="/(\w*)/([^/]*)">\2</a>\n',
                            important_repos.text)
    results = ((match.group(1), match.group(2)) for match in url_matches)
    return itertools.islice(results, 0, 2 * num, 2)


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
    with tempfile.TemporaryDirectory() as corpus_dir:
        for (user, repo) in get_important_repos():
            process_repo(user, repo, corpus_dir)
        with zipfile.ZipFile('corpus.zip', 'w',
                             compression=zipfile.ZIP_DEFLATED) as myzip:
            for langfile in os.listdir(corpus_dir):
                myzip.write(os.path.join(corpus_dir, langfile),
                            os.path.join('corpus', langfile))

if __name__ == '__main__':
    main()
