from pyramid.path import DottedNameResolver
import functools
import inspect
import venusian


ACCEPT_RENDERER_MAP = {
    'json': 'application/json',
    'string': 'text/plain',
}


class MatchdictMapper(object):
    def __init__(self, **kwargs):
        self.view_settings = kwargs
        self.attr = self.view_settings.get('attr')
        self.blacklist = [
            'optional_slash',
        ]

    def __call__(self, view):
        @functools.wraps(view)
        def wrapper(context, request):
            kwargs = request.matchdict.copy()
            for k in self.blacklist:
                if k in kwargs:
                    del kwargs[k]

            if inspect.isclass(view):
                arg_len = len(inspect.getargspec(view.__init__).args)
                if arg_len == 2:
                    inst = view(request)
                elif arg_len == 3:
                    inst = view(context, request)
                else:
                    raise Exception("Class should accept `context` and "
                                    "`request` args only")
                meth = getattr(inst, self.attr)
                return meth(**kwargs)
            else:
                return view(request, **kwargs)

        return wrapper


def add_simple_route(
        config, path, target,
        append_slash=True,
        append_matchdict=True,
        default_accept='text/html',
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
    mapper = config.get_routes_mapper()
    route_name = target.__name__
    route_name_count = 0

    route_kwargs = {}

    if 'accept' in kwargs:
        val = kwargs.pop('accept')
        route_kwargs['accept'] = val
    else:
        # Disable */* by default, only accept 'text/html'
        renderer = kwargs.get('renderer', 'html')
        acceptor = ACCEPT_RENDERER_MAP.get(renderer, default_accept)
        route_kwargs['accept'] = acceptor

    if 'attr' in kwargs:
        route_name += '.' + kwargs['attr']

    routes = {route.name: route for route in mapper.get_routes()}
    orig_route_name = route_name

    while route_name in routes:
        route_name = '%s_%s' % (orig_route_name, route_name_count)
        route_name_count += 1

    current_pregen = kwargs.pop('pregenerator', None)

    def pregen(request, elements, kwargs):
        if 'optional_slash' not in kwargs:
            kwargs['optional_slash'] = ''

        if current_pregen is not None:
            return current_pregen(request, elements, kwargs)
        else:
            return elements, kwargs

    orig_route_prefix = config.route_prefix
    # We are nested with a route_prefix but are trying to
    # register a default route, so clear the route prefix
    # and register the route there.
    if (path == '/' or path == '') and config.route_prefix:
        path = config.route_prefix
        config.route_prefix = ''

    if append_slash:
        path += '{optional_slash:/?}'
        config.add_route(
            route_name, path, pregenerator=pregen,
            **route_kwargs
        )
    else:
        config.add_route(
            route_name, path, pregenerator=current_pregen,
            **route_kwargs
        )

    kwargs['route_name'] = route_name

    if append_matchdict and 'mapper' not in kwargs:
        kwargs['mapper'] = MatchdictMapper

    config.add_view(target, *args, **kwargs)
    config.commit()
    config.route_prefix = orig_route_prefix


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
