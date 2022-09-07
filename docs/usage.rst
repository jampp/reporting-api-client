=====
Usage
=====

To use reporting-api-client in a project::

    from reporting_api_client import ReportingAPIClient

In order to instantiate the client you must provide 2 mandatory parameters, your ``client_id`` and
``client_secret``. If you don't have this credentials, follow the instructions on the
`Authentication section`_ of the `Reporting API documentation`_.

Once you have your hands on a credential pair, you can do something like:

.. code-block:: python

   from reporting_api_client import ReportingAPIClient

   CLIENT_ID = "your_client_id"
   CLIENT_SECRET = "your_client_secret"
   client = ReportingAPIClient(CLIENT_ID, CLIENT_SECRET)


The client has 2 method major methods for query the API:

* :meth:`reporting_api_client.ReportingAPIClient.query`
* :meth:`reporting_api_client.ReportingAPIClient.pivot`

The ``query`` method executes a raw query against the API, returning the results in ``dict`` form if
the request is successfull and raising the corresponding errors if the request fails. It could be
used the following way:

.. code-block:: python

   query = """
       pivot(from: "2022-09-01", to: "2022-09-02") {
          results {
             clicks
          }
       }
   """
   print(client.execute(query))


This method also receives any keyword argument accepted by the `gql.client.execute`_ method.

The ``pivot`` method will build a query according to the parameters, allowing you to define the
parameters of the query instead of building it yourself. In order to replicate the query on the
previous example, one would have to do the following:

.. code-block:: python

   import datetime as dt

   client.pivot(
      from=datetime.datetime(2022, 9, 1),
      to=datetime.datetime(2022, 9, 2),
      metrics=["clicks"],
   )

.. warning::

   In order to use the :meth:`reporting_api_client.ReportingAPIClient.pivot` method you must install
   the library with the pandas optional. More information on :ref:`installation`.


.. _Reporting API documentation: https://developers.jampp.com/docs/reporting-api/
.. _Authentication section: https://developers.jampp.com/docs/reporting-api/#introduction-item-0
.. _gql.client.execute: https://gql.readthedocs.io/en/latest/modules/client.html#gql.client.Client.execute
