from pyramid import testing
from webtest import TestApp

import pytest


def _make_config():
    config = testing.setUp()
    config.include('tomb_routes')
    return config


def _make_app(config=None):
    if config is None:
        config = _make_config()

    app = config.make_wsgi_app()
    return TestApp(app)


@pytest.mark.integration
def test_imperative_config_function():
    from tests.simple_app import my_view

    config = _make_config()
    config.add_simple_route('/path/to/view', my_view, renderer='json')

    response = _make_app(config).get('/path/to/view', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_imperative_config_function_with_dotted_path():
    config = _make_config()
    config.add_simple_route(
        '/path/to/view', 'tests.simple_app.my_view',
        renderer='json'
    )

    response = _make_app(config).get('/path/to/view', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_imperative_config_method():
    from tests.simple_app import MyViewsClass
    config = _make_config()
    config.add_simple_route(
        '/path/to/view',
        MyViewsClass,
        attr='imperative_view',
        renderer='json'
    )

    response = _make_app(config).get('/path/to/view', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_imperative_config_method_with_dotted_path():
    config = _make_config()

    config.add_simple_route(
        '/path/to/view',
        'tests.simple_app.MyViewsClass',
        attr='imperative_view',
        renderer='json'
    )

    response = _make_app(config).get('/path/to/view', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_declarative_config_function():
    config = _make_config()
    config.scan('tests.simple_app')

    response = _make_app(config).get(
        '/path/to/decorated/view/func', status=200
    )

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_declarative_config_method():
    config = _make_config()
    config.scan('tests.simple_app')

    response = _make_app(config).get(
        '/path/to/decorated/view/method', status=200
    )

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_matchdict_method():
    config = _make_config()
    config.scan('tests.simple_app')

    response = _make_app(config).get(
        '/matchdict/sontek/1', status=200
    )

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'sontek', 'bar': '1'}


@pytest.mark.integration
def test_matchdict_class_method():
    config = _make_config()
    config.add_simple_route(
        '/matchdict_class/{name}/{number}',
        'tests.simple_app.MyViewsClass',
        attr='matchdict_view',
        renderer='json'
    )

    response = _make_app(config).get(
        '/matchdict_class/sontek/1', status=200
    )

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'sontek', 'bar': '1'}


@pytest.mark.integration
def test_imperative_route_name():
    # Test that route_name is same as view name
    # See https://github.com/sontek/tomb_routes/pull/5

    from tests.simple_app import my_view

    config = _make_config()
    config.add_simple_route('/path/to/view', my_view, renderer='json')

    route_mapper = config.get_routes_mapper()
    routes = route_mapper.get_routes()

    assert len(routes) == 1
    assert routes[0].name == 'my_view'


@pytest.mark.integration
def test_declarative_route_name():
    config = _make_config()
    config.scan('tests.simple_app')

    route_mapper = config.get_routes_mapper()
    routes = route_mapper.get_routes()
    route_names = [route.name for route in routes]

    assert len(routes) == 7
    assert 'MyViewsClass.imperative_view' in route_names
    assert 'MyViewsClass.matchdict_view' in route_names
    assert 'decorated_view' in route_names
    assert 'matchdict_view' in route_names


@pytest.mark.integration
def test_route_url_with_slash():
    config = _make_config()
    config.scan('tests.simple_app')

    response = _make_app(config).get('/get_url', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {
        'url': 'http://localhost/matchdict/name/1'
    }


@pytest.mark.integration
def test_support_pregenerator_with_slash():
    config = _make_config()

    def pregen(request, elements, kwargs):
        kwargs['name'] = 'boomshaka'
        return elements, kwargs

    def view(request, name, number):
        return {'name': name, 'number': number}

    def view2(request):
        return {'url': request.route_url('view')}

    config = _make_config()
    config.add_simple_route(
        '/test',
        view2,
        renderer='json'
    )

    config.add_simple_route(
        '/test/{name}',
        view,
        pregenerator=pregen
    )

    response = _make_app(config).get(
        '/test',
        status=200,
    )

    assert response.content_type == 'application/json'
    assert response.json == {
        'url': 'http://localhost/test/boomshaka',
    }


@pytest.mark.integration
def test_support_pregenerator_without_slash():
    config = _make_config()

    def pregen(request, elements, kwargs):
        kwargs['name'] = 'boomshaka'
        return elements, kwargs

    def view(request, name, number):
        return {'name': name, 'number': number}

    def view2(request):
        return {'url': request.route_url('view')}

    config = _make_config()
    config.add_simple_route(
        '/test',
        view2,
        renderer='json'
    )

    config.add_simple_route(
        '/test/{name}',
        view,
        pregenerator=pregen,
        append_slash=False
    )

    response = _make_app(config).get(
        '/test',
        status=200,
    )

    assert response.content_type == 'application/json'
    assert response.json == {
        'url': 'http://localhost/test/boomshaka',
    }


@pytest.mark.integration
def test_nested_includes():
    def app_routes(config):
        config.add_simple_route('/', 'tests.simple_app.MyViewsClass',
                                attr='imperative_view',
                                renderer='json')

        config.add_simple_route('/boom', 'tests.simple_app.MyViewsClass',
                                attr='imperative_view',
                                renderer='json')

        config.add_simple_route('/shaka', 'tests.simple_app.MyViewsClass',
                                attr='imperative_view',
                                renderer='json')

    def v1_routes(config):
        config.include(app_routes, route_prefix='/app')

    def include(config):
        config.include(v1_routes, route_prefix='/v1')

    config = _make_config()
    config.include(include)

    response = _make_app(config).get('/v1/app', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}

    response = _make_app(config).get('/v1/app/boom', status=200)
    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_nested_includes_no_append_slash():
    def app_routes(config):
        config.add_simple_route('/', 'tests.simple_app.MyViewsClass',
                                attr='imperative_view',
                                renderer='json',
                                append_slash=False)

    def v1_routes(config):
        config.include(app_routes, route_prefix='/app')

    def include(config):
        config.include(v1_routes, route_prefix='/v1')

    config = _make_config()
    config.include(include)

    response = _make_app(config).get('/v1/app', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_nested_includes_no_append_slash_with_context():
    def app_routes(config):
        config.add_simple_route(
            '/', 'tests.simple_app.MyViewsClassWithContext',
            attr='imperative_view',
            renderer='json',
            append_slash=False
        )

    def v1_routes(config):
        config.include(app_routes, route_prefix='/app')

    def include(config):
        config.include(v1_routes, route_prefix='/v1')

    config = _make_config()
    config.include(include)

    response = _make_app(config).get('/v1/app', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_constructor_count_not_matching():
    config = _make_config()
    config.add_simple_route(
        '/matchdict_class/{name}/{number}',
        'tests.simple_app.BadClass',
        attr='matchdict_view',
        renderer='json'
    )

    with pytest.raises(Exception) as e:
        _make_app(config).get(
            '/matchdict_class/sontek/1', status=200
        )
    msg = "Exception: Class should accept `context` and `request` args only"
    assert msg in str(e)


@pytest.mark.integration
def test_imperative_config_function_root():
    from tests.simple_app import my_view

    config = _make_config()
    config.add_simple_route('/', my_view, renderer='json')

    response = _make_app(config).get('/', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_imperative_config_function_accept_predicates():
    from tests.simple_app import my_view

    config = _make_config()

    config.add_simple_route('/', my_view, renderer='json',
                            accept='application/json')
    config.add_simple_route('/', my_view, renderer='string',
                            accept='text/plain')

    response = _make_app(config).get(
        '/', status=200,
        headers={'accept': 'text/plain'}
    )

    assert response.content_type == 'text/plain'
    assert response.body == b"{'foo': 'bar'}"

    response = _make_app(config).get('/', status=200, headers={
        'Accept': 'application/json'
    })

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_imperative_config_function_accept_predicates_defaults():
    from tests.simple_app import my_view

    config = _make_config()

    config.add_simple_route('/', my_view, renderer='json')
    config.add_simple_route('/', my_view, renderer='string')

    response = _make_app(config).get(
        '/', status=200,
        headers={'accept': 'text/plain'}
    )

    assert response.content_type == 'text/plain'
    assert response.body == b"{'foo': 'bar'}"

    response = _make_app(config).get('/', status=200, headers={
        'Accept': 'application/json'
    })

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}
