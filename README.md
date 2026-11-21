# The World in a Day — Friday 20 November 2026

One day of world news on a single page: a 1024×1024 newspaper front page
generated entirely by a pure–Python-standard-library program.

![make.fun bounty](https://make.fun/badge/news-image-20261120.svg)
![rank](https://make.fun/badge/news-image-20261120/haoye2023/makefun-news-entry/rank.svg)
![reward](https://make.fun/badge/news-image-20261120/haoye2023/makefun-news-entry/reward.svg)

Entry for the make.fun bounty
[“One image sums up the news of 20 Nov 2026”](https://make.fun/bounty/news-image-20261120).

## What is on the page

- A six-figure data strip (Kyiv strikes, the 62–33 Senate vote, $41.7bn in
  border contracts, the −4.5% Nikkei & Kospi close, 16,000 leaked bank
  customers, $2.3bn of GTA 6 sales)
- Three lead stories with program-drawn illustrations: the overnight attack
  on Kyiv, the Trump–Xi–Putin joint peace declaration in Shenzhen, and the
  World Court ruling on Myanmar at The Hague
- Twelve briefs from Brussels to deep space, each with its source named
- An “Also on Friday 20 November” column with fifteen more stories
- A date-check box: every story was first reported on Friday 20 November
  2026 — Thursday's and Saturday's news was left out on purpose

## Running it

```sh
python3 main.py                        # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=. python3 main.py   # writes ./entry.png
```

No dependencies beyond the Python 3 standard library, no network access.
Output is deterministic: two runs produce a byte-identical PNG.

## License

MIT — see [LICENSE](LICENSE).
