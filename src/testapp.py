from exceptions import InvalidCurrencyException
import pytest
import app
import re


class TestApp():

    def test_symbol_ok(self):
        user_curr = 'BTC-USD'
        expected_base_curr = 'BTC-USD'
        response = app.symbol(user_curr)
        assert response['symbol']==expected_base_curr

    def test_symbol_regex_ko(self):
        user_curr = 'BTC-usd'
        with pytest.raises(InvalidCurrencyException) as ex:
            app.symbol(user_curr)

        assert re.match(ex.value.message,'Currency symbol does not match regex requirements')

    def test_symbol_currency_not_exist_ko(self):
        user_curr = 'BTC-XXXXX'
        with pytest.raises(InvalidCurrencyException) as ex:
            app.symbol(user_curr)

        assert re.match(ex.value.message,"Currency does not exist")

    def test_bid_statistics_status_response_ko(self):
        with pytest.raises(InvalidCurrencyException) as ex:
            app.CURRENCY = None
            app.bid_statistics()

        assert re.match(ex.value.message,"Currency symbol is not set")