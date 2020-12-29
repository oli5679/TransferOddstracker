import pytest
import oddschecker_scraper
from moto import mock_s3
import boto3
import gzip

ODDS_CONVERSION_TESTS = [
    ("1/4", 0.80),
    ("1/3", 0.75),
    ("9/1", 0.1),
    ("9", 0.1),
    ("1", 0.5),
]


@pytest.fixture
def prob_scaper():
    return oddschecker_scraper.OddcheckerTransferScraper()


def test_integration_client(prob_scaper):
    prob_scaper.get_all_transfer_probs()
    assert prob_scaper.transfer_data.shape[0] > 0


@pytest.mark.parametrize("test_input,expected", ODDS_CONVERSION_TESTS)
def test_parse_odds(test_input, expected):

    assert oddschecker_scraper.parse_odds(test_input) == expected
