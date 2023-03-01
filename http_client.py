import requests
from pprint import pprint
import json


class VarietyTestingEndpoint:

    request_params = {
        'allow_redirects': True, #for CAS redirects when hitting develop or staging
        'headers': {
            "Authorization": None, # set at runtime
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    }

    def __init__(self, url, token, loud=False):
        self.url = url
        self.loud = loud
        self.request_params['headers']['Authorization'] = f"Bearer {token}"
    
    def show(self, id):
        resp = requests.get(**self.__params(self.url + f"/{id}"))
        self.__log(resp)

    def store(self, payload):
        resp = requests.post(**self.__params(self.url), json=payload)
        self.__log(resp)
        return resp
    
    def update(self, id, payload):
        resp = requests.put(**self.__params(self.url + f"/{id}"), json=payload)
        self.__log(resp)
        return resp

    def index(self):
        resp = requests.get(**self.__params(self.url))
        self.__log(resp)
        return resp

    def delete(self, id):
        resp = requests.delete(**self.__params(self.url + "/{id}"))
        self.__log(resp)
        return resp

    def quiet(self):
        self.loud = False
        return self

    def loud(self):
        self.loud = True
        return self

    def __params(self, url, **kwargs):
        params = self.request_params.copy()
        params['url'] = url
        for key, item in kwargs.items():
            params[key] = item
        return params

    def __log(self, resp: requests.Response):
        m = resp.request.method
        url = resp.request.url
        if self.loud or resp.status_code >= 400:
            print(f"\n{m.upper()} {url}")
            pprint(self.request_params.get('headers'))
            try:
                pprint(json.dumps(json.loads(resp.request.body)))
            except:
                pass
            print("\nResponse:")
            print(f"    Status: {resp.status_code}")
            try:
                print(f"    Reason: {resp.reason}")
            except:
                pass
            if self.loud:
                try:
                    pprint(resp.json())
                except:
                    pass


class VarietyTestingHttpClient:

    uris = [
        "site", "results", "variety", "year"
    ]

    def __init__(self, url, config, loud=False):
        self.__url = url
        self.config = config
        try:
            token = config['api_token']
        except KeyError:
            exit("Your config.json must have an api token")
        self.endpoints = self.__build_clients(token, loud)

    def __build_clients(self, token, loud):
        return dict(zip(self.uris, [VarietyTestingEndpoint(self.__url + '/' + uri, token, loud) for uri in self.uris]))

    def __getattr__(self, __name: str) -> VarietyTestingEndpoint:
        if __name in self.endpoints:
            return self.endpoints[__name]

    def get_year_id(self, year):
        if type(year) == list:
            year = year[0]
        for year_resp in self.year.index().json():
            if str(year) == str(year_resp.get('harvest_year')):
                print(
                    f"Using harvest year publication id {year_resp['id']} for {year} upload")
                return year_resp['id']
        raise Exception(f"No harvest year publication found")
