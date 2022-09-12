====================
Reporting API Client
====================

This is a Python Client for `Jampp's Reporting API`_. For more information, check the `docs`.

Features
========

* Execute Pivots in an user friendly manner.
* Execute raw GraphQL queries against the Reporting API.


Basic Usage
===========

.. code-block:: python

    import os

    from reporting_api_client import ReportingAPIClient


    client = ReportingAPIClient(os.environ["CLIENT_ID"], os.environ["CLIENT_SECRET"])
    query = """{
        pivot(from: "2022-07-01", to: "2022-07-02", granularity: DAILY) {
            results {
                clicks
            }
        }
    }"""

    result = client.query(query)
    print(result)


Executing the above code should output a result similar to the following:

  .. code-block:: console

      $ python example.py
      {'pivot': {'results': [{'clicks': 123456}]}}

.. _`Jampp's Reporting API`: https://developers.jampp.com/docs/reporting-api/
.. _docs: https://developers.jampp.com/docs/reporting-api-client/
