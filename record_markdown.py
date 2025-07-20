import os
from dotenv import load_dotenv


class RecordMarkdown:
    def __init__(self):
        load_dotenv()
        self.md_input_folder = os.getenv("MD_INPUT_FOLDER", "input")
        self.intermediate_folder = os.getenv("INTERMEDIATE_FOLDER", "intermediate")
        self.mp3_output_folder = os.getenv("MP3_OUTPUT_FOLDER", "output")

    def iterate_over_input_md_files(self):
        for input_md in os.listdir(self.md_input_folder):
            filename = os.path.join(self.md_input_folder, input_md)
            print(filename)


if __name__ == "__main__":
    record_markdown = RecordMarkdown()
    record_markdown.iterate_over_input_md_files()
