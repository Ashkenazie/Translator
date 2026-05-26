import tempfile
import unittest
from pathlib import Path

from translator import translate_csv_file, translate_xml_content


class DummyTranslator:
    def translate(self, text: str) -> str:
        return f"DE:{text}"


class TranslatorTests(unittest.TestCase):
    def test_translate_xml_updates_only_valtrnname(self) -> None:
        xml = (
            '<Root Name="Do not translate" ValTrnName="Hello world">'
            '<Item ValTrnName=\'Save\' Message="Keep me" />'
            "</Root>"
        )

        result = translate_xml_content(xml, DummyTranslator())

        self.assertIn('Name="Do not translate"', result)
        self.assertIn('Message="Keep me"', result)
        self.assertIn('ValTrnName="DE:Hello world"', result)
        self.assertIn("ValTrnName='DE:Save'", result)

    def test_translate_csv_updates_only_valtrnname_column(self) -> None:
        csv_content = "Key,ValTrnName,Description\nBTN_SAVE,Save,Should stay\n"

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.csv"
            output_path = Path(tmp) / "output.csv"
            input_path.write_text(csv_content, encoding="utf-8")

            translate_csv_file(input_path, output_path, DummyTranslator())

            result = output_path.read_text(encoding="utf-8")
            self.assertIn("BTN_SAVE,DE:Save,Should stay", result)

    def test_translate_csv_without_target_column_keeps_data(self) -> None:
        csv_content = "Key,Description\nBTN_SAVE,Save label\n"

        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.csv"
            output_path = Path(tmp) / "output.csv"
            input_path.write_text(csv_content, encoding="utf-8")

            translate_csv_file(input_path, output_path, DummyTranslator())

            self.assertEqual(csv_content, output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
