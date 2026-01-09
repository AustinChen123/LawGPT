import requests
import pandas as pd
from bs4 import BeautifulSoup
from tenacity import retry, wait_exponential, stop_after_attempt


@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def html_extraction_de(base_url: str) -> list:
    """
    Enhanced extraction with retry logic and status checks.
    """
    response = requests.get(base_url, timeout=15)
    response.raise_for_status() # Raise error for 4xx/5xx responses
    soup = BeautifulSoup(response.content, 'html.parser')

    # 尋找所有包含 "jnnorm" class 的 div 標籤，這裡是每個法條的主要容器
    norms = soup.find_all('div', class_='jnnorm')

    # 初始化變數
    sections = []

    # 分析 HTML 並提取標題與內容
    for norm in norms:
        current_section = None
        current_content = ""
        # 提取標題，標題由 <h3> 標籤中的內容組成
        title_tag = norm.find('h3')
        if title_tag:
            title_span1 = title_tag.find(
                'span', class_='jnenbez')  # 取得 "Art" 或其他標題部分
            title_span2 = title_tag.find('span', class_='jnentitel')  # 取得標題名稱
            current_section = (title_span1.get_text(strip=True) if title_span1 else '') + \
                ' ' + (title_span2.get_text(strip=True) if title_span2 else '')

        # 提取內容，內容位於 "jurAbsatz" class 的 div 中
        content_divs = norm.find_all('div', class_='jurAbsatz')
        current_content = " ".join([div.get_text(strip=True)
                                   for div in content_divs])

        # 取得 anchor ID 來生成連結
        anchor_tag = norm.find('a', {'name': True})
        if anchor_tag:
            anchor_id = anchor_tag['name']
            link = f"{base_url}#{anchor_id}"
        else:
            link = None
        content_for_save = current_content.strip()
        # 將結果加入 sections 列表
        if (((content_for_save != "") and (content_for_save != "-")) and (link is not None)):
            sections.append({
                'section': current_section,
                'content': content_for_save,
                'link': link
            })

    return sections
