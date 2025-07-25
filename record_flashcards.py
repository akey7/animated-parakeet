import os
import yaml
from kokoro_interface import kokoro_local_tts_to_mp3


def main():
    in_yaml_filename = os.path.join("input", "flashcards.yml")
    out_yaml_filename = os.path.join("output", "recorded_flashcards.yml")
    with open(in_yaml_filename, "r", encoding="utf-8") as in_file:
        flashcards = yaml.safe_load(in_file)
    print(f"Found {len(flashcards)} flashcards")
    for i, flashcard in enumerate(flashcards):
        english = flashcard["english"]
        french = flashcard["french"]
        out_mp3_filename = os.path.join("output", f"{i:0{5}}.mp3")
        flashcard["mp3"] = out_mp3_filename
        print(f"Recording: {french}")
        kokoro_local_tts_to_mp3(
            text=french,
            output_path=out_mp3_filename,
            lang_code="f",
            voice="ff_siwis",
            speed=1.0,
        )
    print("Saving output yaml...")
    with open(out_yaml_filename, "w", encoding="utf-8") as out_file:
        yaml.dump(flashcards, out_file)


if __name__ == "__main__":
    main()
