import re
import requests
import json


def get_repo(user, repo, language):
    url = 'https://api.github.com/repos/{user}/{repo}/'.format(
        user=user, repo=repo)
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

    exit(0)
    requests.get(
        'https://api.github.com/repos/{user}/{repo}/zipball/master'.format(
            user=test[0],
            repo=test[1],
            lang=test[2]))

if __name__ == '__main__':
    main()
