from bs4 import BeautifulSoup
import requests
import gevent
from gevent import monkey, pool
monkey.patch_all()
jobs = []
links = []
p = pool.Pool(10)
urls = [
    'http://www.google.com',
    # ... another 100 urls
]
def get_links(url):
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text)
        links + soup.find_all('a')

if __name__ == '__main__':
    for url in urls:
        jobs.append(p.spawn(get_links, url))
        print(url)
    gevent.joinall(jobs)