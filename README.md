# TransferOddstracker

Basic scraper for oddschecker transfer specials.

Calculates the probability of players moving in transfer window based on odds on 'oddschecker' portal and saves to AWS s3.

Outputs saved here https://transfer-scraper.s3.eu-west-2.amazonaws.com/output/30+most+likely+overall.png

See results saved [here](https://transfer-scraper.s3.eu-west-2.amazonaws.com/output/30+most+likely+overall.png?fbclid=IwAR32gVNXP3E98JHg03I70CDNcYPXg3ju1x5EbaS8LFoCx8yk8-_OTynvyMY)

### Local setup

pip install -r requirements.txt

Configure AWS CLI https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html 

## Running locally

pytest .
python3 oddschecker_scraper.py

## Running on AWS

This can be deployed as lambda function on AWS. Checkout Klayers as a simple way to add Python packages to Lambda function.

https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html

https://github.com/keithrozario/Klayers

## Lambda update

    bash deploy.sh

