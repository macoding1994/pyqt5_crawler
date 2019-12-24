from concurrent.futures import ThreadPoolExecutor
import requests

pool = ThreadPoolExecutor(10)

def task(url):
    response = requests.get(url)
    print(url,response)



url_list = (
    "https://www.bing.com",
    "https://www.shihu.com",
    "https://www.sina.com",
    "https://www.baidu.com",
    "https://www.cnblogs.com",
    "https://music.163.com/#"
)

for url in url_list:
    pool.submit(task,url)

pool.shutdown(wait=True)