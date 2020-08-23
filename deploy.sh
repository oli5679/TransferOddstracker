#!/bin/sh

zip -r transfer_scraper_bundle.zip .

aws lambda update-function-code \
--function-name  transfer-scraper \
    --zip-file fileb://smarket_lambda_bundle.zip

rm smarket_lambda_bundle.zip