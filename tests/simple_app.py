from tomb_routes import simple_route


def my_view(request):
    return {'foo': 'bar'}


@simple_route('/path/to/decorated/view/func', renderer='json')
def decorated_view(request):
    return {'foo': 'bar'}


@simple_route('/matchdict/{name}/{number}', renderer='json')
def matchdict_view(request, name, number):
    return {'foo': name, 'bar': number}


@simple_route('/get_url', renderer='json')
def url_view(request):
    return {'url': request.route_url(
        'matchdict_view',
        name='name',
        number=1,
    )}


class MyViewsClass(object):
    def __init__(self, request):
        self.request = request

    @simple_route('/path/to/decorated/view/method', renderer='json')
    def imperative_view(self):
        return {'foo': 'bar'}

    @simple_route('/matchdict/{name}/{number}', renderer='json')
    def matchdict_view(self, name, number):
        return {'foo': name, 'bar': number}


class MyViewsClassWithContext(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @simple_route('/path/to/decorated/view/method', renderer='json')
    def imperative_view(self):
        return {'foo': 'bar'}

    @simple_route('/matchdict/{name}/{number}', renderer='json')
    def matchdict_view(self, name, number):
        return {'foo': name, 'bar': number}


class BadClass(object):
    def __init__(self, context, request, count):
        self.request = request
        self.context = context
        self.count = count
