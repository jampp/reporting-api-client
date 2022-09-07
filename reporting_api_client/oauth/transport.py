"""Define OAuth transport without session refresh."""
import logging
from typing import Any, Dict, Optional, Union

from requests.adapters import HTTPAdapter, Retry
from requests.cookies import RequestsCookieJar
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from gql.transport.exceptions import (
    TransportAlreadyConnected,
)
from gql.transport.requests import RequestsHTTPTransport


logger = logging.getLogger(__name__)


class NoRefreshOAuth2Session(OAuth2Session):
    """Won't really refresh the token but just create a new one.

    This is needed because auth.jampp.com, doesn't support doing
    token refresh.
    """

    def __init__(self, *, client, client_secret, auth_token_url, **kwargs):
        kwargs.setdefault("token_updater", lambda token: token)
        super().__init__(client=client, auto_refresh_url=auth_token_url, **kwargs)
        self.auth_token_url = auth_token_url
        self.client_secret = client_secret

    def refresh_token(self, *args, **kwargs):
        """
        If the credentials expire, then
        :class:`requests_oauthlib.oauth2_session.OAuth2Session`
        is going to call to the refresh URL using the `refresh_token`
        grant_type. But that isn't supported by the auth server, so this
        changes the logic on the refresh_url to do a new request
        """
        return self.fetch_token(
            token_url=self.auth_token_url,
            client_secret=self.client_secret,
        )


class OAuth2Transport(RequestsHTTPTransport):
    """Sync Transport used to execute queries on servers using OAuth.

    The transport uses the requests library to send HTTP POST requests.

    """

    def __init__(
        self,
        url: str,
        client_id: str,
        client_secret: str,
        auth_token_url: str,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional[Union[Dict[str, Any], RequestsCookieJar]] = None,
        use_json: bool = True,
        timeout: Optional[int] = None,
        verify: Union[bool, str] = True,
        retries: int = 0,
        method: str = "POST",
        **kwargs: Any,
    ):
        """Initialize the transport with the given request parameters.

        :param url: The GraphQL server URL.
        :param client_id: Client id obtained during registration
        :param client_secret: The `client_secret` paired to the `client_id`.
        :param auth_token_url: Token endpoint URL, must use HTTPS.
        :param headers: Dictionary of HTTP Headers to send with the :class:`Request`
            (Default: None).
        :param cookies: Dict or CookieJar object to send with the :class:`Request`
            (Default: None).
        :param use_json: Send request body as JSON instead of form-urlencoded
            (Default: True).
        :param timeout: Specifies a default timeout for requests (Default: None).
        :param verify: Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. (Default: True).
        :param retries: Pre-setup of the requests' Session for performing retries
        :param method: HTTP method used for requests. (Default: POST).
        :param kwargs: Optional arguments that ``request`` takes.
            These can be seen at the `requests`_ source code or the official `docs`_

        .. _requests: https://github.com/psf/requests/blob/master/requests/api.py
        .. _docs: https://requests.readthedocs.io/en/master/

        """
        super().__init__(
            url=url,
            headers=headers,
            cookies=cookies,
            use_json=use_json,
            timeout=timeout,
            verify=verify,
            retries=retries,
            method=method,
            **kwargs,
        )
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_token_url = auth_token_url

    def connect(self):
        if self.session is None:

            # Creating a session that can later be re-use to configure custom mechanisms
            self.session = NoRefreshOAuth2Session(
                client=BackendApplicationClient(self.client_id),
                client_secret=self.client_secret,
                auth_token_url=self.auth_token_url,
            )
            self.session.refresh_token()

            # If we specified some retries, we provide a predefined retry-logic
            if self.retries > 0:
                adapter = HTTPAdapter(
                    max_retries=Retry(
                        total=self.retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=None,
                    )
                )
                for prefix in "http://", "https://":
                    self.session.mount(prefix, adapter)
        else:
            raise TransportAlreadyConnected("Transport is already connected")
