import re
import requests

important_repos = requests.get('https://github.com/repositories')
important_repos.raise_for_status()
url_matches = re.finditer(r'<a href="/(\w*)/([^/]*)">\2</a>\n',
                          important_repos.text)
results = ((match.group(1), match.group(2)) for match in url_matches)
repos = ((user, repo, language) for ((user, repo), (_, language)) in
         zip(results, results))
print(list(repos))
