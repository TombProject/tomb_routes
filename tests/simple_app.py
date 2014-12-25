from tomb_routes import simple_route


def my_view(request):
    return {'foo': 'bar'}


@simple_route('/path/to/decorated/view/func', renderer='json')
def decorated_view(request):
    return {'foo': 'bar'}


@simple_route('/matchdict/{name}/{number}', renderer='json')
def matchdict_view(request, name, number):
    return {'foo': name, 'bar': number}


class MyViewsClass(object):
    def __init__(self, request):
        self.request = request

    @simple_route('/path/to/decorated/view/method', renderer='json')
    def imperative_view(self):
        return {'foo': 'bar'}

    @simple_route('/matchdict/{name}/{number}', renderer='json')
    def matchdict_view(self, name, number):
        return {'foo': name, 'bar': number}
