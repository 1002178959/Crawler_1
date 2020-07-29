import requests


class ProxyHelper(object):
    def __init__(self):
        self.proxy = self._get_proxy_from_mogu()

    def get_proxy(self):
        return self.proxy

    def update_proxy(self, proxy):
        if proxy == self.proxy:
            print('更新了一个proxy', self.proxy)
            self.proxy = self._get_proxy_from_mogu()

    def _get_proxy_from_mogu(self):
        url = 'http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=616f1cbb5a474e7b99ab8dfa1c9e51fa&count=1&expiryDate=0&format=2&newLine=2'
        response = requests.get(url)
        return 'http://' + response.text.strip()


if __name__ == '__main__':
    helper = ProxyHelper()
    print(helper.get_proxy())
