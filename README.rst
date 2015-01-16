tomb_routes
=================================

.. image:: https://img.shields.io/pypi/v/tomb_routes.svg
    :target: https://pypi.python.org/pypi/tomb_routes

.. image:: https://img.shields.io/travis/tomborine/tomb_routes.svg
    :target: https://travis-ci.org/tomborine/tomb_routes

.. image:: https://coveralls.io/repos/tomborine/tomb_routes/badge.png?branch=master
           :target: https://coveralls.io/r/tomborine/tomb_routes?branch=master

Intro
=================================

A set of simple defaults for Pyramid_ routing.

Pyramid's `URL dispatch`_ has separate concepts for **routes** and **views**.
This gives additional flexibility in that you can one route map to multiple
views, using different predicates (e.g.: predicates depending on `Accept`
header, whether request is XHR or not, etc.). In many applications, this
flexibility is not needed and having both **routes** and **views** adds a bit
of complexity and duplication, and reduces DRYness. This module implements some
easy-to-use mechanisms that create a route and a view in one step, resulting in
simpler, easier to understand code. This kind of makes Pyramid's routing look a
bit more like Flask_, albeit without Flask's controversial `thread locals`_.

You can use ``simple_route`` as a decorator:

.. code-block:: python

    from tomb_routes import simple_route
    from pyramid.response import Response

    @simple_route('/hello/{name}')
    def my_route(request, name):
        return Response('Hello %s' % name)

or you can use it from the configurator:

.. code-block:: python

    config.include('tomb_routes')
    config.add_simple_route(
        '/hello/{name}', view_callable,
        renderer='json'
    )


Inspirations
=========================

Frameworks with very simple routing (including so-called "microframeworks") are
nothing new. Here are a few in the Python world:

- minion_
- Klein_
- Flask_

Pyramid is a very powerful and extensible web framework and it's a framework
that we love, but sometimes we want very simple routing. This package brings
the simplified routing from microframeworks to Pyramid, so we can have our cake
and eat it too.


.. _Pyramid: http://www.trypyramid.com/
.. _URL dispatch: http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/urldispatch.html
.. _minion: https://pypi.python.org/pypi/minion
.. _Klein: https://github.com/Twisted/Klein
.. _Flask: http://flask.pocoo.org/
.. _thread locals: http://flask.pocoo.org/docs/latest/design/#thread-locals
