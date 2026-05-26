#!/usr/bin/env python3
import argparse
import csv
import html
import re
from pathlib import Path
from typing import Protocol
from xml.sax.saxutils import escape as xml_escape


class TextTranslator(Protocol):
    def translate(self, text: str) -> str:
        ...


class DeepTranslatorAdapter:
    def __init__(self) -> None:
        try:
            from deep_translator import GoogleTranslator
        except ImportError as exc:  # pragma: no cover - tested via integration usage
            raise RuntimeError(
                "deep-translator is required for runtime translation. "
                "Install it with: pip install deep-translator"
            ) from exc

        self._translator = GoogleTranslator(source="auto", target="de")

    def translate(self, text: str) -> str:
        return self._translator.translate(text)


_VAL_TRN_PATTERN = re.compile(r'(ValTrnName\s*=\s*)(["\'])(.*?)(\2)')


def _should_translate(value: str) -> bool:
    stripped = value.strip()
    return bool(stripped) and any(ch.isalpha() for ch in stripped)


def _translate_value(value: str, translator: TextTranslator) -> str:
    plain_value = html.unescape(value)
    if not _should_translate(plain_value):
        return value

    translated = translator.translate(plain_value)
    return xml_escape(translated, {'"': '&quot;', "'": '&apos;'})


def translate_xml_content(content: str, translator: TextTranslator) -> str:
    def replacer(match: re.Match[str]) -> str:
        prefix, quote, value, suffix = match.groups()
        return f"{prefix}{quote}{_translate_value(value, translator)}{suffix}"

    return _VAL_TRN_PATTERN.sub(replacer, content)


def translate_xml_file(input_path: Path, output_path: Path, translator: TextTranslator) -> None:
    content = input_path.read_text(encoding="utf-8")
    translated = translate_xml_content(content, translator)
    output_path.write_text(translated, encoding="utf-8")


def translate_csv_file(
    input_path: Path,
    output_path: Path,
    translator: TextTranslator,
    column_name: str = "ValTrnName",
) -> None:
    with input_path.open("r", newline="", encoding="utf-8") as infile:
        sample = infile.read(2048)
        infile.seek(0)

        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel

        reader = csv.reader(infile, dialect)
        rows = list(reader)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    header = rows[0]
    try:
        target_index = header.index(column_name)
    except ValueError:
        target_index = None

    if target_index is not None:
        for row in rows[1:]:
            if target_index < len(row):
                row[target_index] = _translate_value(row[target_index], translator)

    with output_path.open("w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, dialect)
        writer.writerows(rows)


def translate_file(input_path: Path, output_path: Path, translator: TextTranslator) -> None:
    suffix = input_path.suffix.lower()
    if suffix == ".xml":
        translate_xml_file(input_path, output_path, translator)
        return
    if suffix == ".csv":
        translate_csv_file(input_path, output_path, translator)
        return

    raise ValueError(f"Unsupported input type: {input_path.suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate ValTrnName values in XML/CSV files into German."
    )
    parser.add_argument("input", type=Path, help="Input XML or CSV file")
    parser.add_argument("output", type=Path, help="Output translated file path")
    args = parser.parse_args()

    translator = DeepTranslatorAdapter()
    translate_file(args.input, args.output, translator)


if __name__ == "__main__":
    main()
