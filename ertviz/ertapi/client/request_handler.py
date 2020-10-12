import requests


class RequestHandler:
    @staticmethod
    def request(ref_url, json=False, stream=False):
        reply = None
        try:
            reply = requests.get(ref_url, stream=stream)
        except requests.ConnectionError:
            return None
        if reply.status_code == 200:
            if json:
                return reply.json()
            return reply
        return None
