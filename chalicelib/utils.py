"""
utils module
"""


def get_base_url(request):
    headers = request.headers
    proto = headers['x-forwarded-proto']
    host = headers['host']
    if request.context.get('stage'):
        stage = request.context['stage']
    else:
        stage = ''
    return f'{proto}://{host}/{stage}'
