Intro
=================================
A set of simple defaults for pyramid routing

You can use the simple router as a decorator:

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
