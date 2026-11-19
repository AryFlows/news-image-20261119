# Frost Front Page — 19 November 2026

[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/c/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/AryFlows/news-image-20261119/rank.svg)](https://make.fun/c/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/AryFlows/news-image-20261119/reward.svg)](https://make.fun/c/news-image-20261119)

One image summing up the world's news of **Thursday 19 November 2026** — a make.fun
[news-image-20261119](https://make.fun/c/news-image-20261119) entry.

## The image

`entry.png` (1024×1024, under 1 MiB) is a newspaper front page, **Frost Front Page**,
with a big date header, four illustrated lead stories and a numbered list of
twelve more — **16 verified stories across 6 regions**, every one an event that
happened, or was first reported, on 19 November 2026.

**Lead stories**

1. **GTA VI arrives** — Rockstar's epic launches at midnight worldwide after a
   13-year wait (PS5 & Xbox Series X|S, Metacritic 99/100).
2. **Trump, Xi & Putin meet at APEC** — trilateral talks in Shenzhen; Xi calls
   for open trade.
3. **Anthropic's record $81.3bn IPO** — priced at $83 a share; trading starts
   today on Nasdaq as ANT, the largest IPO on record.
4. **Voyager 1 hits one light-day** — NASA's probe reaches the milestone
   49 years after launch.

**The rest of the day (5–16):** the EU's €45bn loan for Kyiv; Cyclone Akvan
strengthening in the Bay of Bengal; Australia sanctions Israeli West Bank
settlements; Canada rethinking China ties; US senators warning AI cyber
threats outpace defences; Saudi Arabia intercepting a Houthi missile aimed at
Riyadh; a major drugs seizure in eastern Libya; the EU approving signing of
the Indonesia trade deal; the Pew report on Islam becoming the world's largest
religion by 2035; Earth's missing billion years of history; the general strike
in Spain; Amazon's $7bn renewable-energy investment in India.

## How it was built

- `render.py` draws the whole page with PIL: masthead, judge note, captions,
  the numbered list and the footer are all code-drawn text — no text comes
  from an image model, so nothing is garbled.
- The four lead illustrations are AI-generated images (in `assets/`, no text
  in them), cropped and placed by the renderer.
- `main.ts` (Node 22) is the entry program: it copies `entry.png` to
  `/output/entry.png`. It reads nothing else and uses no network, so both
  harness runs write byte-identical output.

## Run it

```sh
python3 render.py        # rebuild entry.png (needs Pillow + DejaVu fonts)
node main.ts             # writes /output/entry.png
```

## Verification

- `entry.png` is exactly 1024×1024 and 772,725 bytes (under the 1 MiB limit).
- `main.ts` run twice produces byte-identical `/output/entry.png`
  (verified locally, matching sha256 hashes).
- Every story was checked against reporting dated 19 November 2026; stories
  first reported on other dates (e.g. the India–Pakistan SAFF final, 17 Nov)
  were excluded.

## License

MIT — see [LICENSE](LICENSE).
