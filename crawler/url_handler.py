import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def get_doc_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 查找 <abbr> 標籤內含有 "HTML" 的 <a> 標籤
    # 此為我們目標法條的頁面
    a_tag = soup.find('a', text="HTML")
    time.sleep(0.1)
    if a_tag:
        href = a_tag['href']
        return href
    else:
        return None


def generate_target_urls(target_url, endpoint):
    response = requests.get(target_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    anchor_tags = soup.find_all('a')
    endpoint_replace = endpoint + "/"

    links = pd.DataFrame(pd.Series(anchor_tags), columns=["anchor_tags"])
    links = links.iloc[15:-6].reset_index(drop=True)
    links["link"] = links["anchor_tags"].apply(lambda x: x.get("href"))
    links["description"] = links["anchor_tags"].apply(
        lambda x: x.abbr.get("title"))
    links = links[~links['link'].str.endswith('.pdf')].reset_index(drop=True)
    links["full_link"] = links["link"].apply(
        lambda x: endpoint_replace +
        x.split("/")[1] + "/" + get_doc_url(x.replace("./", endpoint_replace))
    )
    return links
