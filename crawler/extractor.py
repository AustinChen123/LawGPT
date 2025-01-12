import requests
import pandas as pd
from bs4 import BeautifulSoup


def html_extraction_de(base_url: pd.DataFrame) -> dict:
    """
    This function will extract certain inforamtion from the gesetze website.
    The function will return a list of dictionary as follows:
    [
    {"section": first section detail,
    "content": law content,
    "link": link to the specific paragraph(by id)},
    {"section": second section detail,
    "content": law content,
    "link": link to the specific paragraph(by id)}
    ]
    For example:
    Given the url:
    https://www.gesetze-im-internet.de/englisch_abgg/englisch_abgg.html

    the element could be:

    <p style="text-align: center; font-weight: bold"><a name="p0017"><!----></a>Section 2<br>Protection of the free exercise of an electoral mandate</p>
    <p><a name="p0018"><!----></a>(1) No one may be prevented from standing as a candidate for a mandate to serve as a Member of the Bundestag or from acquiring, accepting or holding such a mandate.</p>
    <p><a name="p0019"><!----></a>(2) Discrimination at work on the grounds of candidature for or acquisition, acceptance and exercise of a mandate shall be inadmissible.</p>

    The first paragraph is section and section detail.
    The second paragraph is the law content.
    The third paragraph is the law content of the same section of second paragraph.

    And the function will return:
    [
    {'section': 'Section 2:Protection of the free exercise of an electoral mandate',
    'content': '(1) No one may be prevented from standing as a candidate for a mandate to serve as a Member of the Bundestag or from acquiring, accepting or holding such a mandate. (2) Discrimination at work on the grounds of candidature for or acquisition, acceptance and exercise of a mandate shall be inadmissible. (3) Termination of an employment contract or dismissal on grounds of the acquisition, acceptance or exercise of a mandate shall be inadmissible. In all other respects, termination of an employment contract shall only be permitted for a compelling reason. Protection against termination or dismissal shall take effect on the selection of the candidate by the relevant party organ or on submission of the list of nominated candidates. It shall continue to apply for one year after the end of the Member’s term of office.',
    'link': 'https://www.gesetze-im-internet.de/englisch_abgg/englisch_abgg.html#p0017'},
    ]
    """

    response = requests.get(base_url)
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
