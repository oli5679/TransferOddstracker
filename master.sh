SHELL=/bin/bash
BASH_ENV=~/.bashrc_conda

conda activate base

python3 rumour_scraper.py

git add .

git commit -m 'update'

git push
