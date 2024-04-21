from rest_framework.throttling import SimpleRateThrottle


class LowRequestThrottle(SimpleRateThrottle):
    rate = '1/minute'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.id
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }