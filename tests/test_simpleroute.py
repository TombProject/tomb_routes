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

    assert len(routes) == 4
    assert 'MyViewsClass.imperative_view' in route_names
    assert 'MyViewsClass.matchdict_view' in route_names
    assert 'decorated_view' in route_names
    assert 'matchdict_view' in route_names
