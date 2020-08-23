#!/bin/sh

zip -r transfer_scraper_bundle.zip oddschecker_scraper.py

aws lambda update-function-code \
--function-name  transfer-scraper \
    --zip-file fileb://transfer_scraper_bundle.zip

rm transfer_scraper_bundle.zip
