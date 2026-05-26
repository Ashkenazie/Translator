# Translator

Translation helper for 3DXpert localization files.

## Supported input files
- XML
- CSV

## Scope
- Translates only values in `ValTrnName="..."` for XML.
- Translates only the `ValTrnName` column for CSV.
- Keeps all other fields unchanged.

## Usage
```bash
python /home/runner/work/Translator/Translator/translator.py <input.xml|input.csv> <output.xml|output.csv>
```

Runtime translation requires:
```bash
pip install deep-translator
```
