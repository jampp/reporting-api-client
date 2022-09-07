from __future__ import annotations

import datetime
from typing import Any, Dict, Optional, List, Callable

from gql import Client, gql

from reporting_api_client.oauth.transport import OAuth2Transport

try:
    import pandas as pd
except ModuleNotFoundError:
    pd = None


EMPTY_LIST: List[Any] = []


def dict2object(
    a_dict: Dict[str, Any],
    render: Optional[Dict[Any, Callable[[Any], str]]] = None,
) -> str:
    """Print dictionary as GraphQL object.

    :param a_dict: Dictionary to print.
    :param render: Define method to render unsupported object types.

    """
    render = render or {}
    retval = "{ "
    for k, v in a_dict.items():
        retval += f"{k}: "
        if isinstance(v, (str, int, float, list)):
            retval += f"{repr(v)}".replace("'", '"')
        elif isinstance(v, dict):
            retval += dict2object(v)
        else:
            if type(v) in render or {}:
                retval += render[type(v)](v)
            else:
                raise ValueError(f"Can't render type {type(v)}")
    retval += " }"
    return retval


class ReportingAPIClient:
    """Helper Client to execute requests against Jampp's Reporting API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_url: str = "https://reporting-api.jampp.com/v1/graphql",
        auth_token_url: str = "https://auth.jampp.com/v1/oauth/token",
    ) -> None:
        """Initialize the client with the given parameters.

        Parameters
        ----------
        api_url : str
            The URL of the Reporting API endpoint.
        client_id : str
            The Client ID used for authentication.
        client_secret : str
            The `client_secret` paired to the `client_id`.
        api_url : str
            The URL of the Reporting API endpoint.
        auth_token_url : str
            The URL of the Authentication Token creation endpoint.

        """
        self.transport = OAuth2Transport(
            api_url,
            client_id,
            client_secret,
            auth_token_url,
        )

        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=False,
        )

    def query(self, query: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute raw query against Reporting API."""
        return self.client.execute(gql(query), *args, **kwargs)

    def to_frame(self, query: str, *args, **kwargs) -> pd.DataFrame:
        """Execute query and return results as a Pandas DataFrame.

        This method will raise a ``ModuleNotFoundError`` if Pandas is not installed.
        For more information see :ref:`installation`.

        """
        if pd is None:
            raise ModuleNotFoundError("Pandas not installed.")
        return pd.DataFrame.from_records(
            self.query(query, *args, **kwargs)["pivot"]["results"]
        )

    def pivot(
        self,
        from_: datetime.datetime,
        to_: datetime.datetime,
        metrics: List[str],
        dimensions: Optional[List[str]] = None,
        granularity: Optional[str] = None,
        filter_: Optional[Dict[str, Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        cohort_type: Optional[str] = None,
        cohort_window: Optional[datetime.timedelta] = None,
        cleanup: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> pd.DataFrame:
        """Execute pivot against ReportingAPI.

        :param from_: Date from which to execute the report. Will be included in the
            result.
        :param to_: Date up to which to execute the report. Will not be included in the
            report.
        :param metrics: List of `metrics`_ to show on results. If you wish to rename any
            metric on the result, you should state it on the metric name, example:
            ``"open_events: events(event_id: 1)"``.
        :param dimensions: List of `dimensions`_ to group by. If you wish to rename any
            dimension on the result, you should state it on the dimension name, example:
            ``"month: date(granularity: MONTHLY)"``.
        :param granularity: Deprecated. Use `date(granularity: Granularity!)` instead.
        :param filter_: Define a filter to use against the API. Must follow the
            structure of `Filter`_. Example: ``{"appId": {"equals": 10}}``
        :param context: Define a context to use against the API. Must follow the
            structure of `Context`_. Example:
            ``{"sqlTimeZone": "America/Buenos_Aires"}``
        :param cohort_type: Define a `CohortType`_ to use.
        :param cohort_window: Window time delta to use in conjuction with CohortType.
            Does nothing when ``cohort_type`` is not defined.
        :param cleanup: Define a cleanup to use against the API. Must follow the
            structure of `Cleanup`_. Example: ``{"clicks": {"greaterThan": 10}}``


        .. _metrics: https://developers.jampp.com/docs/reporting-api/#definition
                     -PivotMetrics
        .. _dimensions: https://developers.jampp.com/docs/reporting-api/#definition
                     -PivotDimensions
        .. _Filter: https://developers.jampp.com/docs/reporting-api/#definition
                    -Filter
        .. _Context: https://developers.jampp.com/docs/reporting-api/#definition
                     -Context
        .. _CohortType: https://developers.jampp.com/docs/reporting-api/#definition
                        -CohortType
        .. _Cleanup: https://developers.jampp.com/docs/reporting-api/#definition
                     -Cleanup

        """
        pivot_args = []
        pivot_args.append(f'from: "{from_.isoformat()}"')
        pivot_args.append(f'to: "{to_.isoformat()}"')

        if granularity is not None:
            pivot_args.append(f"granularity: {granularity}")

        if filter_ is not None:
            pivot_args.append(f"filter: {dict2object(filter_)}")

        if context is not None:
            pivot_args.append(f"context: {dict2object(context)}")

        if cleanup is not None:
            pivot_args.append(f"cleanup: {dict2object(cleanup)}")

        if cohort_type is not None:
            pivot_args.append(f"cohortType: {cohort_type}")

        if cohort_window is not None:
            pivot_args.append(
                "cohortWindow: { period: HOURS, amount: %s }"
                % (int(cohort_window.total_seconds()) // 3600)
            )

        query = "{ pivot(%s) { results { %s } } }" % (
            ", ".join(pivot_args),
            ", ".join((dimensions or []) + metrics),
        )
        return self.to_frame(query)
