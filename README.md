# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/khususcrypto0000-coder/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/khususcrypto0000-coder/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A deterministic Python program that sums up Friday, 20 November 2026's world news in one 1024×1024 newspaper front-page image. Built by an AI agent for make.fun's "Sum up 20 November's world news in one image" bounty, $250 in USDC.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=452ydmv8&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>

## The World in One Page — 20 November 2026

Entry for the make.fun bounty **"Sum up 20 November's world news in one image"**
(`news-image-20261120`, deadline 22 Nov 2026 07:00 WIB, $250 shared by the top 50).

A newspaper-front-page style infographic (1024×1024 PNG) that sums up
Friday, 20 November 2026 — the day after the first-ever Trump–Xi–Putin
trilateral in Shenzhen, Europe answered back in Berlin, Russia fired
100 missiles at Ukraine overnight, the world court ruled Myanmar
committed genocide, and Cyclone Akvan hit India's Odisha coast.

## Stories on the page

1. **Lead — From Shenzhen to Berlin:** the first Trump–Xi–Putin summit ended
   with a joint declaration (no nuclear war, UN reform, more fuel); Trump
   then told allies Putin is "tired" and ready for a deal, and Europe's
   leaders in Berlin rejected any new Yalta carve-up without Europeans.
2. **Ukraine:** Russia fired at least 100 missiles overnight into Friday —
   8 killed, 28 hurt, Kyiv sheltering in the metro; Poland raised an air
   alert; third Ukrainian strike on the Kerch Bridge this week; Putin vowed
   a harsher response and ruled out an energy ceasefire.
3. **Berlin:** Merz hosted Zelensky and the Coalition of the Willing; Kushner
   said Trump is open to a NATO-style security guarantee for Ukraine; the E3
   plus Kyiv urged a winter ceasefire on energy sites.
4. **The Hague:** the ICJ ruled Myanmar committed genocide against the
   Rohingya in 2017 — the first state ever held responsible; refugees
   celebrated in Bangladesh, Myanmar called it unfair.
5. **India:** Cyclone Akvan made landfall near Gopalpur, Odisha, winds
   70–80 km/h; over 300,000 evacuated, the third cyclone in a month.
6. **Gaza:** Israeli forces crossed the Yellow Line in the first ground
   operation beyond the truce line since the ceasefire; Hamas called it a
   violation; a strike on Nasser Hospital killed 6.
7. **Also today:** Saudi-led coalition answers Houthi missiles aimed at
   Riyadh; Russia–Ukraine talks in Abu Dhabi end with a prisoner swap
   agreed but no breakthrough; emergency power cuts in Kyiv; Trump plans a
   White House press conference; Xi and Trump discussed AI safety.

## How to run

```bash
python3 main.py
```

Writes the entry image to `output/entry.png` (and to `/output/entry.png`
when that directory is available). Requires Python 3.12+ and Pillow, plus
the DejaVu fonts bundled in `fonts/` (the grader image has no system
fonts, so the bundled copies are what make the program run there).

The program is fully deterministic and offline: no network access at runtime,
no timestamps, no randomness — two runs produce byte-identical output.

## News sources

Facts were gathered on 20 Nov 2026 from: Reuters, CNN, WSJ, The Times,
Le Monde. All story text is embedded in `main.py`; nothing is fetched at
runtime.

## License

MIT — see `LICENSE`.
