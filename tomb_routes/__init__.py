from pyramid.path import DottedNameResolver
import inspect
import venusian


class MatchdictMapper(object):
    def __init__(self, **kwargs):
        self.view_settings = kwargs
        self.attr = self.view_settings.get('attr')
        self.blacklist = [
            'optional_slash',
        ]

    def __call__(self, view):
        def wrapper(context, request):
            kwargs = request.matchdict.copy()
            for k in self.blacklist:
                if k in kwargs:
                    del kwargs[k]

            if inspect.isclass(view):
                inst = view(request)
                meth = getattr(inst, self.attr)
                return meth(**kwargs)
            else:
                return view(request, **kwargs)

        return wrapper


def add_simple_route(
        config, path, target,
        append_slash=True,
        append_matchdict=True,
        *args, **kwargs
):
    """Configuration directive that can be used to register a simple route to
    a view.

    Examples:

    with view callable::

        config.add_simple_route(
            '/path/to/view', view_callable,
            renderer='json'
        )

    with dotted path to view callable::

        config.add_simple_route(
            '/path/to/view', 'dotted.path.to.view_callable',
            renderer='json'
        )
    """

    target = DottedNameResolver().maybe_resolve(target)

    route_name = target.__name__
    if 'attr' in kwargs:
        route_name += '.' + kwargs['attr']

    if append_slash:
        path += '{optional_slash:/?}'

    config.add_route(route_name, path)
    kwargs['route_name'] = route_name

    if append_matchdict and 'mapper' not in kwargs:
        kwargs['mapper'] = MatchdictMapper

    config.add_view(target, *args, **kwargs)


class simple_route(object):
    """ A decorator that can be used to register a simple route to
    a view.

    Example:

    @simple_route('/path/to/view', renderer='json')
    def view_callable(request):
        return {'message': 'Hello'}
    """

    def __init__(self, path, *args, **kwargs):
        """Constructor just here to accept parameters for decorator"""
        self.path = path
        self.args = args
        self.kwargs = kwargs

    def __call__(self, wrapped):
        """Attach the decorator with Venusian"""
        args = self.args
        kwargs = self.kwargs

        def callback(scanner, _name, wrapped):
            """Register a view; called on config.scan"""
            config = scanner.config

            # pylint: disable=W0142
            add_simple_route(config, self.path, wrapped, *args, **kwargs)

        info = venusian.attach(wrapped, callback)

        if info.scope == 'class':  # pylint:disable=E1101
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if kwargs.get('attr') is None:
                kwargs['attr'] = wrapped.__name__

        return wrapped


def includeme(config):
    """Function that gets called when client code calls config.include"""
    config.add_directive('add_simple_route', add_simple_route)
