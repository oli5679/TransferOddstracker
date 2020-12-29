# TransferOddstracker

Basic scraper for oddschecker transfer specials.

Calculates the probability of players moving in transfer window based on odds on 'oddschecker' portal and saves to AWS s3.

Outputs saved here https://transfer-scraper.s3.eu-west-2.amazonaws.com/output/30+most+likely+overall.png

## Getting Started

git clone https://github.com/oli5679/TransferOddstracker/

### Local setup

pip install -r requirements.txt

Configure AWS CLI https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html 

Create target S3 bucket and update 'target bucket'

## Running locally

python3 rumour_scraper.py

## Running on AWS

This can be deployed as lambda function on AWS. Checkout Klayers as a simple way to add Python packages to Lambda function.

https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html

https://github.com/keithrozario/Klayers

