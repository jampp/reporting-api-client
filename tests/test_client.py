import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock


from reporting_api_client.client import dict2object, ReportingAPIClient


class TestClient(TestCase):
    @patch("reporting_api_client.client.OAuth2Transport")
    def setUp(self, transport_mock):
        self.client = ReportingAPIClient(
            "client_id",
            "client_secret",
            api_url="api_url",
            auth_token_url="auth_token_url",
        )
        self.transport_mock = transport_mock

    def test_dict2object(self):
        self.assertEqual(dict2object({"a": "b"}), '{ a: "b" }')
        self.assertEqual(dict2object({"a": 1}), "{ a: 1 }")
        self.assertEqual(dict2object({"a": 1.1}), "{ a: 1.1 }")
        self.assertEqual(dict2object({"a": {"b": "c"}}), '{ a: { b: "c" } }')

    def test_init(self):
        self.transport_mock.assert_called_with(
            "api_url", "client_id", "client_secret", "auth_token_url"
        )

    def test_pivot(self):
        to_frame_mock = MagicMock()
        self.client.to_frame = to_frame_mock
        self.client.pivot(
            from_=datetime.datetime(2022, 1, 1),
            to_=datetime.datetime(2022, 1, 2),
            metrics=["clicks", "installs"],
            granularity="DAILY",
            filter_={"campaignId": {"isIn": [1, 2, 3]}},
            context={"sqlTimeZone": "America/Buenos_Aires"},
            dimensions=["date", "app"],
            cohort_type="TOUCH",
            cohort_window=datetime.timedelta(hours=10),
            cleanup={"clicks": {"greaterThan": 1}},
        )
        query = to_frame_mock.call_args[0][0]
        self.assertRegex(query, r"from: \"2022-01-01T00:00:00\"")
        self.assertRegex(query, r"to: \"2022-01-02T00:00:00\"")
        self.assertRegex(query, r"granularity: DAILY")
        self.assertRegex(query, r"filter: \{ campaignId: \{ isIn: \[1, 2, 3\] \} \}")
        self.assertRegex(
            query, r"context: \{ sqlTimeZone: \"America\/Buenos_Aires\" \}"
        )
        self.assertRegex(query, r"cohortType: TOUCH")
        self.assertRegex(query, r"cohortWindow: { period: HOURS, amount: 10 }")
        self.assertRegex(query, r"results \{ date, app, clicks, installs \}")
