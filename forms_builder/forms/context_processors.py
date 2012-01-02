# For the template tag, we need to have access to the request object

def request(request):
    return {'request': request}
