import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from datetime import datetime
import boto3
import io
import requests
import lxml
from lxml import html

matplotlib.use("agg")
plt.style.use("seaborn")
s3 = boto3.resource("s3")
BUCKET = "transfer-scraper"

MARKETS_X_PATH = (
    "/html/body/div[1]/div[2]/div/div/div/div/div/div[1]/section[2]/div/div/ul[3]"
)

"""
Lambda function to get transfer rumours from oddscheckers, saving to s3 (data and charts)
"""


def parse_odds(odds_val):
    """
    Turns odds string into numeric odds

    Args:
        odds_val (str): string with odds

    Returns:
        prob (number): probability of transfer (number)
    """
    odds_str = str(odds_val)
    if "/" in odds_str:
        num, denom = odds_str.split("/")
        return int(denom) / (int(denom) + int(num))
    else:
        try:
            return 1 / (float(odds_str) + 1)
        except:
            return np.nan


class OddcheckerTransferScraper:
    """
    Client for getting latest transfer rumours from oddschecker.com

    Methods:
        get_all_transfer_probs: 
            returns implied probabilities for all transfers
    """

    def __init__(self):
        self.base = "https://www.oddschecker.com"
        self.transfer_data = pd.DataFrame()

    def get_all_transfer_probs(self):
        """
        Gets all next club transfer odds

        Returns:
            transfer_data (df): dataframe with transfer probs
        """
        self._get_links()
        for i, l in enumerate(self.transfer_links):
            print(f"{l} \n {i+1}/{len(self.transfer_links)} \n")
            try:
                transfer_probs = self._parse_link(l)
                self.transfer_data = self.transfer_data.append(
                    transfer_probs, sort=False
                )
            except Exception as e:
                print("parsing failed")
                print(e)
        return self.transfer_data

    def _get_links(self):
        """
        Gets all links from player special page 'markets' table with 'club-after' or 'to-sign-for' in link
       
        Returns:
            transfer_links (list): list of transfer market pages
        """
        url = f"{self.base}/football/player-specials"
        response = requests.get(url)
        tree = lxml.html.fromstring(response.content)
        # Find the transfer rumours
        markets = tree.xpath(MARKETS_X_PATH)
        links = [self.base + l[2] for l in markets[0].iterlinks()]
        self.transfer_links = [
            l
            for l in links
            if "club-after-summer-transfer-window" in l or "to-sign-for" in l
        ]
        assert len(self.transfer_links) > 0
        return self.transfer_links

    def _parse_link(self, link):
        """
        Gets and transforms odds from page

        Args:
            link (string): page to get odds from

        Returns
            prob_df (dataframe): transfer odds for player
        """
        tables = pd.read_html(link)
        # Odds table seems to be last table on page
        odds_df = tables[-1]
        # Remove crazy long column names
        odds_df.columns = [""] * len(odds_df.columns)
        # Transpose - clubs along axis
        clean_df = odds_df.T.rename(columns=odds_df.T.iloc[0])
        # Calculate lowest odds - most likely
        long_df = pd.DataFrame(clean_df.applymap(parse_odds).min()).reset_index()
        # Add in column names, including player name
        long_df.columns = ["destination", "probability"]
        long_df["player"] = link.split("/")[-2].replace("-", " ").title()
        # add probability and date
        long_df["date"] = datetime.now().date()
        return long_df


def make_bar_chart(df, filter_var, y_var, filter_val, title):
    filter_df = df.loc[
        (df[filter_var] == filter_val) & (df.probability > 0)
    ].sort_values(by="probability", ascending=True)
    if filter_df.shape[0] > 2:
        plt.subplots(figsize=(20, 15))
        ax = plt.barh(filter_df[y_var], filter_df["probability"])
        locs, labels = plt.xticks()
        plt.setp(labels, rotation=90)
        plt.title(title, {"fontsize": 20})
        key = f"output/{filter_var}s/{filter_val}.png"
        img_data = io.BytesIO()
        plt.savefig(img_data, format="png")
        img_data.seek(0)
        s3.Bucket(BUCKET).put_object(Body=img_data, ContentType="image/png", Key=key)
        plt.close()


def plot_most_likely(df, n):
    most_likely = (
        df.loc[~df.destination.str.contains("To Stay|To Leave|Any|Not to sign")]
        .sort_values(by="probability", ascending=True)
        .tail(n)
    )
    most_likely["transfer"] = most_likely.player + " - " + most_likely["destination"]
    plt.subplots(figsize=(20, 15))
    ax = plt.barh(most_likely["transfer"], most_likely["probability"],)
    plt.title(f"{n} most likely Transfers \n", {"fontsize": 20})
    img_data = io.BytesIO()
    plt.savefig(img_data, format="png")
    plt.close()
    img_data.seek(0)
    key = f"output/{n} most likely overall.png"
    s3.Bucket(BUCKET).put_object(Body=img_data, ContentType="image/png", Key=key)


def make_charts(df):
    """
    Makes bar charts and saves to s3
    """
    for dest in df.loc[
        ~df.destination.str.contains("To Stay|To Leave|Any|Not to sign"), "destination"
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


def lambda_handler(event=None, context=None):
    print(f"event {event} context {context}")

    print("scraping links")
    link_scrap = OddcheckerTransferScraper()
    combined_df = link_scrap.get_all_transfer_probs()

    print("making charts")
    make_charts(combined_df)
    csv_buffer = io.StringIO()
    key = f"data/{datetime.now().date()}.csv"
    s3.Object(BUCKET, key).put(Body=csv_buffer.getvalue())
    print("finished")
    return "success"


if __name__ == "__main__":
    lambda_handler()
