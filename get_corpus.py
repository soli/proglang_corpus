import re
import requests
import json
import io
import zipfile

BASE_URL = 'https://api.github.com/repos/{user}/{repo}/'


def get_repo(user, repo, language):
    url = BASE_URL.format(user=user, repo=repo)
    get_languages(url, language)
    get_data(url)


def get_data(url):
    data = requests.get(url + 'zipball/master')
    data.raise_for_status()
    zip = zipfile.ZipFile(io.BytesIO(data.content))
    print(zip.namelist())


def get_languages(url, language):
    r = requests.get(url + 'languages')
    r.raise_for_status()
    languages = json.loads(r.text)
    print(languages)
    total = sum(languages.values())
    print(language + ': ' + str(languages.get(language)) + ' / ' + str(total))


def main():
    important_repos = requests.get('https://github.com/repositories')
    important_repos.raise_for_status()
    url_matches = re.finditer(r'<a href="/(\w*)/([^/]*)">\2</a>\n',
                            important_repos.text)
    results = ((match.group(1), match.group(2)) for match in url_matches)
    repos = ((user, repo, language) for ((user, repo), (_, language)) in
            zip(results, results))
    test = list(repos)[0]
    get_repo(*test)


if __name__ == '__main__':
    main()
