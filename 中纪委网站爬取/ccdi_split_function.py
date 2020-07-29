import requests
import re
from lxml import etree
from urllib import parse
from bs4 import BeautifulSoup
from multiprocessing import Pool
from multiprocessing import Manager


# 拼接URL的时候，最好使用urllib中的parse中的urljoin函数

headers = {
    'Referer': 'http://www.ccdi.gov.cn/special/jdbg3/index.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',

}

def parse_detailed_bxgd_fbwt(url):
    print(url)
    # 爬虫的第三步
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    # 爬虫的第四步
    html_ele = etree.HTML(response.text)
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


# 八项规定详情页
def parse_detailed_bxgd(url, url_function_list):
    res_list = list(parse_detailed_bxgd_fbwt(url))
    res_list.append('八项规定')
    return res_list


# 腐败问题详情页
def parse_detailed_fbwt(url, url_function_list):
    res_list = list(parse_detailed_bxgd_fbwt(url))
    res_list.append('腐败问题')
    return res_list


# 纠风案例详情页
def parse_detailed_jfal(url, url_function_list):
    # 爬虫的第三步
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    # 爬虫的第四步
    html_ele = etree.HTML(response.text)
    title = html_ele.xpath('//h2[@class="tit"]/text()')[0].strip()
    sourse = html_ele.xpath('//h3[@class="daty"]/em[1]/text()')[0].replace('来源：', '')
    time = html_ele.xpath('//h3[@class="daty"]/em[2]/text()')[0].replace('发布时间：', '')
    content = html_ele.xpath('//div[@class="TRS_Editor"]/div//text()')
    content = [item.strip() for item in content if item.strip()]
    content_str = '\n'.join(content)
    # yield [title, sourse, time, content_str]
    return [title, sourse, time, content_str, '纠风案例']


# 列表页获取详情页URL
def get_detailed_page_url(url, url_function_list):
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
            # res = parse_detailed_bxgd(detailed_page_url)
            url_function_list.put((detailed_page_url, parse_detailed_bxgd))
        elif 'sffbwt_jdbg3' in detailed_page_url:
            # res = parse_detailed_fbwt(detailed_page_url)
            url_function_list.put((detailed_page_url, parse_detailed_fbwt))
        else:
            # res = parse_detailed_jfal(detailed_page_url)
            url_function_list.put((detailed_page_url, parse_detailed_jfal))
        # print(res)


# 列表页数获取
def parse_list_page(url, url_function_list):
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    res_match = re.search('createPageHTML\((\d+)', response.text)
    page_num = int(res_match.group(1))
    url_function_list.put((url, get_detailed_page_url))
    for i in range(1, page_num):
        url_next_page = url + 'index_' + str(i) + '.html'
        url_function_list.put((url_next_page, get_detailed_page_url))
        break


def get_all_province_url(url, url_function_list):
    response = requests.get(url, verify=False, headers=headers)
    response.encoding = 'utf-8'
    three_d = ['fjbxgdwt_jdbg3', 'sffbwt_jdbg3', 'sfjds_jdbg3']
    # 第四步
    soup = BeautifulSoup(response.text, 'lxml')
    base_url = 'http://www.ccdi.gov.cn/special/jdbg3/{}/{}/'
    a_tag_list = soup.select('ul:nth-of-type(3)>li>a')
    for a_tag in a_tag_list:
        prov = a_tag['href'].replace('.', '').replace('/', '')
        for item in three_d:
            url = base_url.format(prov, item)
            url_function_list.put((url, parse_list_page))
            break
        break


if __name__ == '__main__':
    # 这里需要使用Queue（队列）
    queue = Manager().Queue()
    url = 'http://www.ccdi.gov.cn/special/jdbg3/'
    queue.put((url, get_all_province_url))
    # 添加进程池
    # 一般来说进程的个数小于等于CPU数量×2
    pool = Pool(2)
    res_list = []

    while True:
        try:
            url, func = queue.get(timeout=5)
        except:
            break

        res = pool.apply_async(func=func, args=(url, queue))
        res_list.append(res)

    for res in res_list:
        ret = res.get()
        if ret:
            print(ret)
    pool.close()
    pool.join()
