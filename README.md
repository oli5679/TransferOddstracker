# TransferOddstracker

Basic scraper for oddschecker transfer specials - calculates the probability of players moving in window.

See results saved [here](https://transfer-scraper.s3.eu-west-2.amazonaws.com/output/30+most+likely+overall.png?fbclid=IwAR32gVNXP3E98JHg03I70CDNcYPXg3ju1x5EbaS8LFoCx8yk8-_OTynvyMY)

## Getting Started

    git clone https://github.com/oli5679/TransferOddstracker/
    pip install requirements.txt
    pytest .

(requires AWS cli, and s3 bucket with same name as BUCKET)

## Running 

    python3 rumour_scraper.py

## Lambda update

    bash deploy.sh

