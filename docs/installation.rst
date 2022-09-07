.. highlight:: shell
.. _installation:

============
Installation
============

Stable release
==============

To install reporting-api-client, run this command in your terminal:

.. code-block:: console

    pip install jampp_reporting_api_client


This is the preferred method to install reporting-api-client, as it will always install the most
recent stable release.

You can also install the optional ``pandas`` dependency to use DataFrames, by doing:

.. code-block:: console

   pip install jampp_reporting_api_client[pandas]


From sources
============

The sources for ``reporting-api-client`` can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    git clone git://github.com/jampp/reporting_api_client


Once you have a copy of the source, you can install it with:

.. code-block:: console

    pip install -e .[dev]

.. _Github repo: https://github.com/jampp/reporting_api_client
