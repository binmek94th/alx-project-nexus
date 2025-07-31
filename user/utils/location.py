import httpagentparser


def parse_user_agent(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return httpagentparser.detect(user_agent)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
