def get_base_url(request):
    """Helper for getting a current base URL of application. It can provide to
    suppor a lot of environments without pre-hardcoded stages
    """
    # TODO: find a way to get stage and region
    gapi_id = request.context['apiId']
    stage = 'api'
    region = 'eu-north-1'
    return f'https://{gapi_id}.execute-api.{region}.amazonaws.com/{stage}'


def clean_message(message):
    return message.lower().replace(" ", "").replace("\n", "")
