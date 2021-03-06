# Requires installing `selenium` and `webdriver_manager` via pip

import os
import requests
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager


class TheGlobeMailScarper:
    FUNDS_URL = "https://www.theglobeandmail.com/investing/markets/funds/{}/"
    STOCKS_URL = "https://www.theglobeandmail.com/investing/markets/stocks/{}/"

    def __init__(self):
        self.profile_path = "D:/dev/Upwork-Assignments/stock-market-CMS/ff_profile"
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)

        self.firefox_options = webdriver.FirefoxOptions()
        self.firefox_options.add_argument("--headless")
        self.firefox_options.add_argument("--log-level=3")

    def check_availability(self, symbol=None):
        if symbol is None:
            return None
        funds_check = requests.get(self.FUNDS_URL.format(symbol))
        if funds_check.status_code == 200:
            return "funds"
        stocks_check = requests.get(self.STOCKS_URL.format(symbol))
        if stocks_check.status_code == 200:
            return "stock"
        return None

    def _cast_data(self, value, cast_type):
        try:
            return cast_type(value)
        except:
            return None

    def scrap_funds(self, driver, ticker):

        driver.get(self.FUNDS_URL.format(ticker.ticker))
        last_price_el = driver.find_element_by_xpath(
            '//barchart-field[@name="lastPrice"]'
        )
        prev_price_el = driver.find_element_by_xpath(
            '//barchart-field[@name="previousPrice"]'
        )
        company_name_el = driver.find_element_by_xpath('//span[@id="instrument-name"]')
        symbol_el = driver.find_element_by_xpath('//span[@id="instrument-symbol"]')
        ytd_exchange_el = driver.find_element_by_xpath(
            '//td[@data-barchart-field="returnYtd"]'
        )

        return {
            "latestPrice": self._cast_data(last_price_el.text, float),
            "previousClose": self._cast_data(prev_price_el.text, float),
            "companyName": company_name_el.text,
            "symbol": symbol_el.text,
            "ytdChange": self._cast_data(ytd_exchange_el.text.replace("%", ""), float),
            "shares_owned": ticker.shares_owned,
            "market_value": round(
                float(ticker.shares_owned) * float(last_price_el.text), 2
            ),
        }

    def scrap_stock(self, driver, ticker):
        driver.get(self.STOCKS_URL.format(ticker.ticker))
        last_price_el = driver.find_element_by_xpath(
            '//barchart-field[@name="lastPrice"]'
        )
        prev_price_el = driver.find_element_by_xpath(
            '//barchart-field[@name="previousPrice"]'
        )
        high_price_1y = driver.find_element_by_xpath(
            '//barchart-field[@name="highPrice1y"]'
        )
        low_price_1y = driver.find_element_by_xpath(
            '//barchart-field[@name="lowPrice1y"]'
        )
        company_name_el = driver.find_element_by_xpath('//span[@id="instrument-name"]')
        symbol_el = driver.find_element_by_xpath('//span[@id="instrument-symbol"]')
        print(last_price_el.text)
        return {
            "latestPrice": self._cast_data(last_price_el.text, float),
            "previousClose": self._cast_data(prev_price_el.text, float),
            "companyName": company_name_el.text,
            "symbol": symbol_el.text,
            "week52Low": self._cast_data(low_price_1y.text, float),
            "week52High": self._cast_data(high_price_1y.text, float),
            "shares_owned": ticker.shares_owned,
            "market_value": round(
                float(ticker.shares_owned) * float(last_price_el.text), 2
            ),
        }

    def scrap_bulk(self, tickers):
        driver = webdriver.Firefox(
            executable_path=GeckoDriverManager().install(),
            options=self.firefox_options,
        )

        ret = []
        for ticker, fund_type in tickers:
            if fund_type == "funds":
                data = self.scrap_funds(driver, ticker)
                ret.append(data)
            else:
                data = self.scrap_stock(driver, ticker)
                ret.append(data)

        driver.quit()

        return ret

    def scrap_data(self, ticker, fund_type):
        firefox_profile = webdriver.FirefoxProfile(self.profile_path)
        driver = webdriver.Firefox(
            executable_path=GeckoDriverManager().install(),
            options=self.firefox_options,
            firefox_profile=firefox_profile,
        )
        if fund_type == "funds":
            data = self.scrap_funds(driver, ticker)
        else:
            data = self.scrap_stock(driver, ticker)

        driver.quit()

        return data
