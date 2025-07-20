import os
import re
from dotenv import load_dotenv


class RecordMarkdown:
    def __init__(self):
        load_dotenv()
        self.md_input_folder = os.getenv("MD_INPUT_FOLDER", "input")
        self.intermediate_folder = os.getenv("INTERMEDIATE_FOLDER", "intermediate")
        self.mp3_output_folder = os.getenv("MP3_OUTPUT_FOLDER", "output")

    def iterate_over_input_md_files(self):
        for filename in os.listdir(self.md_input_folder):
            input_md_filename = os.path.join(self.md_input_folder, filename)
            intermediate_txt_filename = os.path.join(self.intermediate_folder, filename.replace(".md", ".txt"))
            with open(input_md_filename, "r", encoding="utf-8") as f:
                md_text = f.read()
            plain_text = self.clean_markdown(md_text)
            with open(intermediate_txt_filename, "w", encoding="utf-8") as f:
                f.write(plain_text)
            print(input_md_filename, "->", intermediate_txt_filename)

    def clean_markdown(self, md_text):
        """
        1) Remove YAML front matter (--- … ---),
        2) Drop image references (inline & reference style),
        3) Strip out tables (any block of ≥2 lines with pipes),
        4) Strip URLs from links [text](url) → text,
        5) Remove HTML tags,
        6) Remove bold (**text** / __text__) and italic (*text* / _text_) markers.
        """
        md_text = re.sub(
            r'\A---\s*\n.*?\n---\s*\n',
            '',
            md_text,
            flags=re.DOTALL
        )
        md_text = re.sub(
            r'!\[.*?\]\(.*?\)|!\[[^\]]*\]\[[^\]]*\]',
            '',
            md_text
        )
        md_text = re.sub(
            r'^\s*\[[^\]]+\]:\s*.*\.(?:png|jpe?g|gif|svg)(?:\s*".*?")?\s*$\n?',
            '',
            md_text,
            flags=re.MULTILINE | re.IGNORECASE
        )
        md_text = re.sub(
            r'(?:^\s*\|.*\|\s*$\n?){2,}',
            '',
            md_text,
            flags=re.MULTILINE
        )
        md_text = re.sub(
            r'\[([^\]]+)\]\([^)]+\)',
            r'\1',
            md_text
        )
        md_text = re.sub(
            r'<[^>]+>',
            '',
            md_text
        )
        md_text = re.sub(
            r'(\*\*|__)(.*?)\1',
            r'\2',
            md_text,
            flags=re.DOTALL
        )
        md_text = re.sub(
            r'(\*|_)(.*?)\1',
            r'\2',
            md_text,
            flags=re.DOTALL
        )
        md_text = re.sub(
            r'\[\^\d+\]',
            '',
            md_text
        )
        md_text = md_text.replace("l' ", "l'").replace("L' ", "L'")
        return md_text

if __name__ == "__main__":
    record_markdown = RecordMarkdown()
    record_markdown.iterate_over_input_md_files()
