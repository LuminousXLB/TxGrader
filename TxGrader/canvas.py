import re

import httpx

from .token import get_token

__all__ = ["http", "CanvasHttp"]


class CanvasHttp:
    def __init__(self, base_url, token=None) -> None:
        if not token:
            token = get_token()

        self._http = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": "Bearer {}".format(token),
                "Content-Type": "application/json",
            },
        )

    def get(self, url, *, params=None, follow_redirects=True) -> httpx.Response:
        resp = self._http.request(
            "GET", url, params=params, follow_redirects=follow_redirects
        )
        resp.raise_for_status()
        return resp

    def post(self, url, *, data=None, json=None, params=None):
        return self._http.request("POST", url, data=data, json=json, params=params)

    def put(self, url, *, data=None, json=None, params=None):
        return self._http.request("PUT", url, data=data, json=json, params=params)

    def paginated(self, url, *, key=None, params=None):
        reg = re.compile('<(?P<url>http\S+)>; rel="(?P<rel>\S+)"')

        while url:
            resp = self.get(url, params=params)

            data = resp.json()[key] if key else resp.json()
            for item in data:
                yield item

            link = {
                k: v
                for v, k in (
                    reg.match(l).groups() for l in resp.headers.get("link").split(",")
                )
            }
            url = None if link["last"] == link["current"] else link["next"]


http = CanvasHttp(base_url="https://canvas.nus.edu.sg/")
