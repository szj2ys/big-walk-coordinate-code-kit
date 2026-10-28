"""Decode fixed-width grid codes without rounding or losing leading zeros."""

import argparse
import csv
import io
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


def decode_code(value):
    """A four-digit code stores a scale reading in hundredths."""
    value = value.strip()
    if not re.fullmatch(r"[0-9]{4}", value):
        raise ValueError(f"Expected exactly four ASCII digits, got {value!r}")
    return f"{int(value[:2])}.{value[2:]}"


def encode_reading(value):
    try:
        reading = Decimal(value)
    except InvalidOperation:
        raise ValueError(f"Invalid decimal reading: {value!r}") from None
    if not reading.is_finite() or not Decimal(0) <= reading <= Decimal("99.99"):
        raise ValueError("A reading must be between 0 and 99.99 inclusive")
    if reading.is_zero():
        return "0000"
    # Inspect stored digits directly; Decimal arithmetic can round to its context.
    _, digits, exponent = reading.as_tuple()
    shift = exponent + 2
    if shift < 0:
        fractional_digits = -shift
        if fractional_digits >= len(digits) or any(digits[-fractional_digits:]):
            raise ValueError("More than two decimal places would require rounding")
        digits = digits[:-fractional_digits]
        shift = 0
    hundredths = int("".join(map(str, digits))) * 10**shift
    return f"{hundredths:04d}"


def record(side_code, bottom_code, label=""):
    side, bottom = decode_code(side_code), decode_code(bottom_code)
    return {
        "label": label,
        "side_code": side_code.strip(),
        "bottom_code": bottom_code.strip(),
        "side_reading": side,
        "bottom_reading": bottom,
    }


def load_pairs(pairs, csv_path):
    records = []
    if csv_path:
        with Path(csv_path).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not {"side_code", "bottom_code"}.issubset(reader.fieldnames or []):
                raise ValueError("CSV requires side_code and bottom_code columns")
            for line, row in enumerate(reader, 2):
                if None in row or row.get("side_code") is None or row.get("bottom_code") is None:
                    raise ValueError(f"CSV line {line}: malformed or missing field")
                try:
                    records.append(record(row["side_code"], row["bottom_code"], row.get("label", "")))
                except ValueError as error:
                    raise ValueError(f"CSV line {line}: {error}") from None
    for pair in pairs:
        parts = pair.split("/")
        if len(parts) != 2:
            raise ValueError(f"Use SIDE/BOTTOM, for example 4166/1899; got {pair!r}")
        records.append(record(*parts))
    return records


def render(records, output_format):
    if output_format == "json":
        return json.dumps(records, ensure_ascii=False, indent=2)
    fields = ["label", "side_code", "bottom_code", "side_reading", "bottom_reading"]
    if output_format == "csv":
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
        return stream.getvalue().rstrip("\n")
    lines = ["SIDE CODE  BOTTOM CODE  SIDE READING  BOTTOM READING  LABEL"]
    lines.extend(
        f"{r['side_code']:9}  {r['bottom_code']:11}  {r['side_reading']:12}  "
        f"{r['bottom_reading']:14}  {r['label']}" for r in records
    )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pairs", nargs="*", metavar="SIDE/BOTTOM")
    parser.add_argument("--csv", type=Path, help="Read side_code,bottom_code,label columns")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--encode", nargs=2, metavar=("SIDE_READING", "BOTTOM_READING"))
    args = parser.parse_args(argv)
    if args.encode and (args.pairs or args.csv):
        parser.error("--encode cannot be combined with codes or --csv")
    try:
        if args.encode:
            result = " / ".join(encode_reading(v) for v in args.encode)
        else:
            if not (args.pairs or args.csv):
                parser.error("Provide a code pair, --csv, or --encode")
            result = render(load_pairs(args.pairs, args.csv), args.format)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
