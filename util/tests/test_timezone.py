import unittest
from datetime import datetime, timezone

from django.test import SimpleTestCase

try:  # pragma: no cover - exercised indirectly by skip behaviour
    from util import tz_aware_datetime
except ModuleNotFoundError:  # python-magic missing in the execution environment
    tz_aware_datetime = None


@unittest.skipIf(tz_aware_datetime is None, "python-magic dependency is not installed")
class TZAwareDateTimeTests(SimpleTestCase):

    def test_epoch_integer_converted_to_utc(self):
        epoch = 1_700_000_000

        aware = tz_aware_datetime(epoch)

        self.assertEqual(aware.tzinfo, timezone.utc)
        self.assertEqual(aware, datetime.fromtimestamp(epoch, tz=timezone.utc))

    def test_string_with_offset_normalised_to_utc(self):
        date_str = '2024-02-01T12:30:00+02:00'

        aware = tz_aware_datetime(date_str)

        expected = datetime(2024, 2, 1, 10, 30, tzinfo=timezone.utc)
        self.assertEqual(aware, expected)

    def test_naive_datetime_assumed_utc(self):
        naive = datetime(2024, 2, 1, 12, 30, 45)

        aware = tz_aware_datetime(naive)

        self.assertEqual(aware.tzinfo, timezone.utc)
        self.assertEqual(aware, datetime(2024, 2, 1, 12, 30, 45, tzinfo=timezone.utc))

    def test_naive_string_assumed_utc(self):
        date_str = '2024-02-01T12:30:45'

        aware = tz_aware_datetime(date_str)

        self.assertEqual(aware.tzinfo, timezone.utc)
        self.assertEqual(aware, datetime(2024, 2, 1, 12, 30, 45, tzinfo=timezone.utc))
