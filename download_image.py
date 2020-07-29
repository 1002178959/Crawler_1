import requests
import os
from lxml import etree
from proxyhelper import ProxyHelper

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Referer': 'https://www.mzitu.com/',
}


def get_all_list_url(url):
    print('正在处理最外层URL:', url)
    print('--' * 30)
    response = requests.get(url, headers=headers)
    html_ele = etree.HTML(response.text)
    # //ul[@id="pins"]/li/a/@href
    href_list = html_ele.xpath('//ul[@id="pins"]/li/a/@href')
    for href in href_list:
        get_detailed_page_url(href)

    next_page_ele = html_ele.xpath('//a[@class="next page-numbers"]/@href')
    if next_page_ele:
        get_all_list_url(next_page_ele[0])


def get_detailed_page_url(url):
    response = requests.get(url, headers=headers)
    html_ele = etree.HTML(response.text)
    try:
        page_num = html_ele.xpath('//div[@class="pagenavi"]/a[last()-1]/span/text()')[0]
        for i in range(int(page_num)):
            detailed_url = url + '/' + str(i + 1)
            get_image_url(detailed_url)
            print('正在下载...' + detailed_url)

    except:
        print('get_detailed_page_url fail')


def get_image_url(url):
    response = requests.get(url, headers=headers)
    html_ele = etree.HTML(response.text)
    # /html/body/div[2]/div[1]/div[3]/p/a/img
    src = html_ele.xpath('//div[@class="main-image"]/p/a/img/@src')[0]
    download_image(src, url)


def download_image(url, referer):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Referer': referer,
    }
    response = requests.get(url, headers=headers)

    filename = downloaddir + '/' + url.split('/')[-1]
    with open(filename, 'wb') as f:
        f.write(response.content)


if __name__ == '__main__':
    downloaddir = 'F:\\殷鸿剑的小秘密'
    if not os.path.exists(downloaddir):
        os.mkdir(downloaddir)
    helper = ProxyHelper()
    proxy = helper.get_proxy()
    url = 'https://www.mzitu.com'
    get_all_list_url(url)
