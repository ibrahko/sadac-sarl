from django.http import HttpResponseForbidden

BLOCKED_PATHS = [
    '.env', '.php', '.sh', '.sql', '.bak',
    'phpmyadmin', 'adminer', 'setup', 'install',
    'WEB-INF', 'META-INF', 'secret', 'backup',
    'xmlrpc', 'wp-login', 'wp-admin',
]

BLOCKED_USER_AGENTS = [
    'masscan', 'zgrab', 'nmap', 'sqlmap',
    'nikto', 'dirbuster', 'hydra',
]


class BlockBotsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.lower()
        ua   = request.META.get(
            'HTTP_USER_AGENT', ''
        ).lower()

        # Bloque les chemins suspects
        for blocked in BLOCKED_PATHS:
            if blocked in path:
                return HttpResponseForbidden(
                    "Accès interdit.",
                    content_type="text/plain"
                )

        # Bloque les user-agents de scanners
        for blocked_ua in BLOCKED_USER_AGENTS:
            if blocked_ua in ua:
                return HttpResponseForbidden(
                    "Accès interdit.",
                    content_type="text/plain"
                )

        return self.get_response(request)
