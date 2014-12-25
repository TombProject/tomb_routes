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
        '/path/to/view', MyViewsClass.imperative_view,
        renderer='json'
    )

    response = _make_app(config).get('/path/to/view', status=200)

    assert response.content_type == 'application/json'
    assert response.json == {'foo': 'bar'}


@pytest.mark.integration
def test_imperative_config_method_with_dotted_path():
    config = _make_config()

    config.add_simple_route(
        '/path/to/view', 'tests.simple_app.MyViewsClass.imperative_view',
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
