import requests
import json

class Handler:
    def __init__(self):
        pass

    def get(self, url, headers):
        request_headers = {**headers}
        print(f"[http][get] Url: {url}", flush=True)
        resp = requests.get(url, headers=request_headers)
        if resp.ok:
            try:
                return json.loads(resp.content)
            except:
                print(
                    f"[http][get][error] Exception occured for url: {url}", flush=True
                )
        else:
            print(
                f"[http][get][error] Exception occured for url: {url}, status_code: {resp.status_code}, resp: {json.loads(resp.content)}",
                flush=True,
            )
            return resp.status_code

    def get_file(self, url, headers):
        print(f"[http][get_file] Url: {url} Headers: {headers}", flush=True)
        resp = requests.get(
            url, headers={**headers, "Accept": "application/pdf"}, stream=True
        )
        resp.raise_for_status()
        if resp.ok:
            try:
                return resp.content
            except:
                print(
                    f"[http][get_file][error] Exception occured for url: {url}",
                    flush=True,
                )
        else:
            print(
                f"[http][get_file][error] Exception occured for url: {url}, status_code: {resp.status_code}, resp: {json.loads(resp.content)}",
                flush=True,
            )
            return resp.status_code

    def post(self, url, headers, payload):
        request_headers = {**headers}
        print(f"[http][post] Url: {url}", flush=True)
        resp = requests.post(url, headers=request_headers, json=payload)
        if resp.ok:
            try:
                return json.loads(resp.content)
            except:
                print(
                    f"[http][post][error] Exception occured for url: {url}", flush=True
                )
        else:
            print(
                f"[http][post][error] Exception occured for url: {url}, status_code: {resp.status_code}, resp: {json.loads(resp.content)}",
                flush=True,
            )
            return resp.status_code

    def put(self, url, headers, payload):
        request_headers = {**headers}
        print(f"[http][put] Url: {url}", flush=True)
        resp = requests.put(url, headers=request_headers, json=payload)
        if resp.ok:
            try:
                return json.loads(resp.content)
            except:
                print(
                    f"[http][put][error] Exception occured for url: {url}", flush=True
                )
        else:
            print(
                f"[http][put][error] Exception occured for url: {url}, status_code: {resp.status_code}, resp: {json.loads(resp.content)}",
                flush=True,
            )
            return resp.status_code