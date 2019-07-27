from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FF_Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from time import sleep
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from IPython.display import clear_output
import shutil
import os
import click
import logging
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class LinkScraper:
    def __init__(self, headless):
        options = FF_Options()

        if headless == 'headless':
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(
            options=options)
        self.transfer_df = pd.DataFrame()

    def _parse_odds(self, odds_val):
        odds_str = str(odds_val)
        if "/" in odds_str:
            num, denom = odds_str.split("/")
            return int(num) / int(denom)
        else:
            try:
                return float(odds_str)
            except:
                return np.nan

    def _wait_for_element(self, id, pause_time=60):
        WebDriverWait(self.driver, pause_time).until(
            EC.presence_of_element_located((By.ID, id))
        )

    def _parse_link(self, link):
        try:
            self.driver.get(link)
            sleep(1)
            self._wait_for_element(id="t1")
            tables = pd.read_html(self.driver.page_source)
            # Odds table seems to be last table on page
            odds_df = tables[-1]
            # Remove crazy long column names
            odds_df.columns = [""] * len(odds_df.columns)
            # Transpose - clubs along axis
            clean_df = odds_df.T.rename(columns=odds_df.T.iloc[0])
            # Calculate lowest odds - most likely
            long_df = pd.DataFrame(clean_df.applymap(
                self._parse_odds).min()).reset_index()
            # Add in column names, including player name
            long_df.columns = ["destination", "odds"]
            long_df["player"] = link.split("/")[-2].replace("-", " ").title()
            # add probability and date
            long_df["probability"] = 1 / (1 + long_df["odds"])
            long_df["date"] = datetime.now().date()
            self.transfer_df = self.transfer_df.append(long_df, sort=False)
        except Exception as e:
            logging.info('parsing failed')
            logging.info(e)

    def _get_links(self):
        url = "https://www.oddschecker.com/football/player-specials"
        self.driver.get(url)
        self._wait_for_element(id="outrights")
        # Find the transfer rumours
        markets = self.driver.find_element_by_xpath(
            '//*[@id="outrights"]/div/ul[2]'
        ).find_elements_by_tag_name("li")
        links = [m.find_element_by_tag_name(
            "a").get_attribute("href") for m in markets]
        self.transfer_links = [
            l for l in links if "club-after-summer-transfer-window" in l
        ]
        assert len(self.transfer_links) > 0

    def get_and_parse_all_links(self):
        try:
            self._get_links()
            for i, l in enumerate(self.transfer_links):
                clear_output()
                logging.info(f"{l} \n {i+1}/{len(self.transfer_links)} \n")
                self._parse_link(l)
            return self.transfer_df
        except Exception as e:
            raise e
        finally:
            self.driver.quit()


def make_bar_chart(df, filter_var, y_var, filter_val, title, show_flag=False):
    filter_df = df.loc[
        (df[filter_var] == filter_val) & (df.probability > 0)
    ].sort_values(by="probability", ascending=False)
    if filter_df.shape[0] > 2:
        plt.subplots(figsize=(20, 15))
        ax = sns.barplot(data=filter_df, y=y_var, x="probability", orient="h")
        locs, labels = plt.xticks()
        plt.setp(labels, rotation=90)
        ax.set_title(title, {"fontsize": 20})
        plt.savefig(f"output/{filter_var}s/{filter_val}.png")
        if show_flag:
            plt.show()
        plt.close()


def plot_most_likely(df, n):
    most_likely = (
        df.loc[~df.destination.str.contains(
            "To Stay|To Leave|Any|Not to sign")]
        .sort_values(by="probability", ascending=False)
        .head(n)
    )
    most_likely["transfer"] = most_likely.player + \
        " - " + most_likely["destination"]
    plt.subplots(figsize=(20, 15))
    ax = sns.barplot(data=most_likely, y="transfer",
                     x="probability", orient="h")
    ax.set_title(f"{n} most likely Transfers \n", {"fontsize": 20})
    plt.savefig(f"output/{n} most likely overall.png")


def make_charts(df):
    try:
        shutil.rmtree("output/players")
        shutil.rmtree("output/destinations")
        logging.info("previous output removed")
    except FileNotFoundError:
        logging.info("no previous output directories")
    os.mkdir("output/players")
    os.mkdir("output/destinations")
    for dest in df.loc[
        ~df.destination.str.contains(
            "To Stay|To Leave|Any|Not to sign"), "destination"
    ].unique():
        make_bar_chart(
            df=df,
            filter_var="destination",
            y_var="player",
            filter_val=dest,
            title=f"{dest} Transfer Targets \n",
        )

    for player in df.player.unique():
        make_bar_chart(
            df=df,
            filter_var="player",
            y_var="destination",
            filter_val=player,
            title=f"{player} Destinations \n",
        )

    plot_most_likely(df, 30)


def main(headless, log_mode):
    if log_mode == 'file':
        logging.basicConfig(filename='app.log', filemode='w',
                            format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
    sns.set_style("whitegrid")

    logging.info("started scraping links")
    link_scrap = LinkScraper(headless=headless)
    combined_df = link_scrap.get_and_parse_all_links()
    logging.info("started making charts")
    make_charts(combined_df)
    combined_df.to_csv(f"output/data/{datetime.now().date()}.csv")
    logging.info("finished")


if __name__ == "__main__":
    main(headless=False, log_mode='print')
