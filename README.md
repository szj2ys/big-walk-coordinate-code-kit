# Coordinate Code Kit

A small offline utility for reading four-digit grid codes, preserving leading zeros, and sharing a checked worksheet with teammates. Python 3.9 or later; no dependencies, network access, tracking, or account required.

## Use it

```console
python grid_codes.py 4166/1899 0025/0900
python grid_codes.py --csv examples.csv --format csv
python grid_codes.py --csv examples.csv --format json
python grid_codes.py --encode 41.66 18.99
```

The first command shows `41.66` on the side scale and `18.99` on the bottom scale. The reverse command returns `4166 / 1899`. A batch file can add a `label` column for your own observations. Malformed rows stop the whole conversion before any result is printed, so a partial worksheet is not mistaken for a complete one.

## What the conversion means

Each code is exactly four ASCII digits. The last two digits represent hundredths: `0025` means `0.25`; `0900` means `9.00`. Axis names are explicit to avoid swapping the side and bottom readings. The tool does not use floating-point arithmetic or silently round a reading.

This is notation conversion, not geolocation. It does not identify a place, infer compass directions, validate an in-game clue, or supply a map. `0000` and `9999` are valid notation boundaries, not claims about reachable places. All example rows except `4166 / 1899` are synthetic.

## A team workflow

1. Copy the code exactly, including zeros, and note which code belongs to each scale.
2. Decode it and have another player read the result back.
3. Locate the two readings on the map you actually have.
4. Add a short observation to the CSV label after checking the location in play.

For the illustrated Big Walk context behind the published example, see [Big Walk Guide's map and coordinate explanation](https://thebigwalk.world/en/map). That unofficial source includes its own evidence limits. This utility contains no map data or game artwork and is independent of House House and Panic.

## Check it

```console
python -m unittest -v
```

The checks exercise every four-digit round trip, strict validation, batch errors, and command-line output. They verify the conversion, not game mechanics.

Created for Big Walk Guide with AI assistance. Released under the MIT license.
