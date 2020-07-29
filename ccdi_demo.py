import requests
import re
from lxml import etree
from urllib import parse
from bs4 import BeautifulSoup

# 拼接URL的时候，最好使用urllib中的parse中的urljoin函数
headers = {
    'Referer': 'http://www.ccdi.gov.cn/special/jdbg3/bj_bgt/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',

}


def parse_detailed_bxgd_fbwt(url):
    import time
    import random
    temp = random.randint(1, 2)
    time.sleep(int(temp))
    # 爬虫的第三步
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    # 爬虫的第四步
    html_ele = etree.HTML(response.text)
    try:
        title = html_ele.xpath('//h2[@class="tit"]/text()')[0].strip()
        sourse = html_ele.xpath('//h3[@class="daty"]/em[1]/text()')[0].replace('来源：', '')
        time = html_ele.xpath('//h3[@class="daty"]/em[2]/text()')[0].replace('发布时间：', '')
        content = html_ele.xpath('//p/text()')
        if len(content) > 1:
            if not re.search('^\d+', content[0].strip()):
                content = content[1:]
            for cont in content:
                if cont.strip():
                    yield [title, sourse, time, cont.strip()]
        else:
            yield [title, sourse, time, content[0].strip()]
    except:
        parse_detailed_bxgd_fbwt(url)


# 八项规定详情页
def parse_detailed_bxgd(url):
    res_list = list(parse_detailed_bxgd_fbwt(url))
    res_list.append('八项规定')
    return res_list


# 腐败问题详情页
def parse_detailed_fbwt(url):
    res_list = list(parse_detailed_bxgd_fbwt(url))
    res_list.append('腐败问题')
    return res_list


# 纠风案例详情页
def parse_detailed_jfal(url):
    print(url)
    # 爬虫的第三步
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    # 爬虫的第四步
    html_ele = etree.HTML(response.text)
    try:
        title = html_ele.xpath('//h2[@class="tit"]/text()')[0].strip()
        sourse = html_ele.xpath('//h3[@class="daty"]/em[1]/text()')[0].replace('来源：', '')
        time = html_ele.xpath('//h3[@class="daty"]/em[2]/text()')[0].replace('发布时间：', '')
        content = html_ele.xpath('//div[@class="TRS_Editor"]/div//text()')
        content = [item.strip() for item in content if item.strip()]
        content_str = '\n'.join(content)
        # yield [title, sourse, time, content_str]
        return [title, sourse, time, content_str, '纠风案例']
    except:
        parse_detailed_jfal(url)


# 列表页获取详情页URL
def get_detailed_page_url(url):
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    # 找到所有的li标签
    li_str_list = re.findall('<li class="fixed">(.*?)</li>', response.text, re.S)
    # 由于循环内需要使用正则表达式，最好是在外面定义类，compile
    pat = re.compile('<a href="(.*)" target="_blank"')
    for li_str in li_str_list:
        res_match = pat.search(li_str)
        detailed_page_url = parse.urljoin(url, res_match.group(1))
        if 'fjbxgdwt_jdbg3' in detailed_page_url:
            res = parse_detailed_bxgd(detailed_page_url)
        elif 'sffbwt_jdbg3' in detailed_page_url:
            res = parse_detailed_fbwt(detailed_page_url)
        else:
            res = parse_detailed_jfal(detailed_page_url)
        print(res)


# 列表页数获取
def parse_list_page(url):
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    res_match = re.search('createPageHTML\((\d+)', response.text, re.S)
    page_num = int(res_match.group(1))
    get_detailed_page_url(url)
    for i in range(1, page_num):
        url_next_page = url + 'index_' + str(i) + '.html'
        get_detailed_page_url(url_next_page)


def get_all_province_url(url):
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    three_d = [ 'sfjds_jdbg3']
    # 第四步
    soup = BeautifulSoup(response.text, 'lxml')
    base_url = 'http://www.ccdi.gov.cn/special/jdbg3/{}/{}/'
    a_tag_list = soup.select('ul:nth-of-type(3)>li>a')
    for a_tag in a_tag_list:
        prov = a_tag['href'].replace('.', '').replace('/', '')
        for item in three_d:
            url = base_url.format(prov, item)
            parse_list_page(url)

        break


if __name__ == '__main__':
    url = 'http://www.ccdi.gov.cn/special/jdbg3/'
    get_all_province_url(url)
    # url='http://www.ccdi.gov.cn/special/jdbg3/bj_bgt/fjbxgdwt_jdbg3/201805/t20180523_172409.html'
    # print(list(parse_detailed_bxgd_fbwt(url)))
