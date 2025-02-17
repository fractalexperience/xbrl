import requests


headers = {
    'User-Agent': 'Sample Company Name AdminContact@samplecompanydomain.com'
}


class GetRequest:
    def __init__(self, url, headers=headers):
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code != requests.codes.ok:
            raise RequestException('{}: {}'.format(response.status_code, response.text))
        
        self.response = response

class RequestException(Exception):
    pass