from .proxies import Proxy
from .headers import Headers

class UserMaster:
    """Provides users according to spec if needed."""
    def designee(self):
        return User.from_randagent_proxyrotator()            

class User:
    proxy_rotator = Proxy.from_rotator()
    def __init__(self, proxy: Proxy, headers: Headers):
        self.proxy = proxy
        self.headers = headers
    
    @classmethod
    def from_randagent_proxyrotator(cls):
        return cls(User.proxy_rotator, Headers.random())
