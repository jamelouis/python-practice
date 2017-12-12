from bs4 import BeautifulSoup as bs
import re

from urllib.request import urlopen
import requests


def get_subdomain(html):
    soup = bs(html,'html.parser')
    return [(li.a['data-attr1'], li.a['href']) for li in soup.findAll('li', {'class':'chapter-item'})]

def get_problems(html):
    soup = bs(html,'html.parser')

    challenges_div = soup.findAll('div', { 'class' : 'challenges-list-view'})

    page_list = []
    problem_list = []

    for challenge_block in challenges_div:
        title = challenge_block.h4.get_text()
        #print(challenge_block.footer.get_text())
        difficulty = re.search(r'Difficulty: (Easy|Medium|Hard|Advanced)', challenge_block.footer.get_text())
        if difficulty:
            print(title, difficulty.group(1))
            problem_list.append((title, difficulty.group(1)))

    page_items = soup.findAll('li', { 'class' : 'page-item' } )

    for page in page_items:
        print(page.a['href'])
        page_list.append(page.a['href'])

    return page_list, problem_list

def get_all_problems(session, headers, domain_name, relative_url):
    pages_set = set()
    
    base_url = 'https://www.hackerrank.com'

    html = session.get(base_url + relative_url, headers=headers)
    
    page_list, problem_list = get_problems(html.text)
    
    problems = []

    for page in page_list:
        html = session.get(base_url + page, headers=headers)
        page_list_temp, problem_list = get_problems(html.text)
        problems += problem_list
    
    with open(domain_name+'.csv', 'w') as f:
        f.write('problem,difficulty\n')
        for prob in problems:
            f.write(prob[0]+','+prob[1]+'\n')

if __name__ == '__main__':
    
    base_url = 'https://www.hackerrank.com/domains/mathematics/'

    session = requests.Session()
    header = { 'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebkit 537.36 (KHTML, like Gecko) Chrome",
                'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}

    req = session.get(base_url, headers=header)
    domains = get_subdomain(req.text)
    print(domains)
    for domain in domains:
        get_all_problems(session, header, domain[0], domain[1])


