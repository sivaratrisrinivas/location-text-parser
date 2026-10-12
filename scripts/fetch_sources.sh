#!/bin/bash
# Re-fetch the public sources used by the eval (pages change; the saved copies in sources/ are what was labeled on 2026-10-13).
cd "$(dirname "$0")/../sources"
curl -s https://hacker-news.firebaseio.com/v0/item/50056667.json > hn_50056667.json
curl -s https://hn.algolia.com/api/v1/items/49922569 > hn_thread_49922569.json
for p in fse ai; do curl -sL -A Mozilla/5.0 https://matcha.fm/apply/$p -o matcha_$p.html; done
curl -sL -A Mozilla/5.0 https://matcha.fm/careers -o matcha_careers.html
