import os
import random
import os
import shutil
import sys
import yaml

# from kokoro_interface import kokoro_local_tts_to_mp3
from elevenlabs_interface import elevenlabs_tts_to_mp3
import genanki


def create_flashcards(in_yaml_filename):
    with open(in_yaml_filename, "r", encoding="utf-8") as in_file:
        flashcards = yaml.safe_load(in_file)
    print(f"Found {len(flashcards)} flashcards")
    for i, flashcard in enumerate(flashcards):
        english = flashcard["en"]
        french = flashcard["fr"]
        out_mp3_filename = os.path.join("output", "mp3", f"{i:0{5}}.mp3")
        flashcard["mp3"] = out_mp3_filename
        flashcard["answer"] = f"{french} / {english}"
        print(f"Recording: {french}")
        # kokoro_local_tts_to_mp3(
        #     text=french,
        #     output_path=out_mp3_filename,
        #     lang_code="f",
        #     voice="ff_siwis",
        #     speed=1.0,
        # )
        elevenlabs_tts_to_mp3(text=french, filename=out_mp3_filename)
    return flashcards


def create_audio_multiple_choice_deck(
    cards_data,
    deck_name="Audio Multiple Choice Deck",
    output_filename="audio_mc_deck.apkg",
):
    """
    Create an Anki deck with MP3 audio questions and multiple choice answers.

    Args:
        cards_data: List of dictionaries with 'mp3' (filepath) and 'answer' (text) keys
        deck_name: Name of the Anki deck
        output_filename: Output filename for the .apkg file

    Returns:
        str: Path to the created .apkg file
    """

    # Generate unique IDs for the model and deck
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)

    # Create a model (note type) for audio multiple choice cards
    audio_mc_model = genanki.Model(
        model_id,
        "Audio Multiple Choice Model",
        fields=[
            {"name": "Audio"},
            {"name": "CorrectAnswer"},
            {"name": "Option1"},
            {"name": "Option2"},
            {"name": "Option3"},
            {"name": "Option4"},
            {"name": "Option5"},
            {"name": "CorrectPosition"},  # Which option (1-5) is correct
        ],
        templates=[
            {
                "name": "Audio MC Card",
                "qfmt": """
                <div style="text-align: center; margin: 20px;">
                    <h3>Listen to the audio:</h3>
                    {{Audio}}
                    <div style="text-align: left; max-width: 600px; margin: 30px auto; font-size: 18px;">
                        <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>A)</strong> {{Option1}}
                        </div>
                        <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>B)</strong> {{Option2}}
                        </div>
                        <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>C)</strong> {{Option3}}
                        </div>
                        <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>D)</strong> {{Option4}}
                        </div>
                        <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>E)</strong> {{Option5}}
                        </div>
                    </div>
                </div>
                """,
                "afmt": """
                <div style="text-align: center; margin: 20px;">
                    <h3>Audio:</h3>
                    {{Audio}}
                    <div style="text-align: left; max-width: 600px; margin: 30px auto; font-size: 18px;">
                        <div id="option1" style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>A)</strong> {{Option1}}
                        </div>
                        <div id="option2" style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>B)</strong> {{Option2}}
                        </div>
                        <div id="option3" style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>C)</strong> {{Option3}}
                        </div>
                        <div id="option4" style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>D)</strong> {{Option4}}
                        </div>
                        <div id="option5" style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
                            <strong>E)</strong> {{Option5}}
                        </div>
                    </div>
                    <hr>
                    <h3 style="color: green; margin-top: 20px;">Correct Answer: {{CorrectAnswer}}</h3>
                </div>
                
                <script>
                // JavaScript to highlight correct answer
                (function() {
                    var correctPos = {{CorrectPosition}};
                    if (correctPos >= 1 && correctPos <= 5) {
                        var correctOption = document.getElementById('option' + correctPos);
                        if (correctOption) {
                            correctOption.style.backgroundColor = '#90EE90';
                            correctOption.style.fontWeight = 'bold';
                        }
                    }
                })();
                </script>
                """,
            },
        ],
    )

    # Create the deck
    deck = genanki.Deck(deck_id, deck_name)

    # Create a package to include media files
    package = genanki.Package(deck)

    # Keep track of media files
    media_files = []

    # Extract all answers for generating wrong options
    all_answers = [card["answer"] for card in cards_data]

    # Add cards to the deck
    for idx, card_data in enumerate(cards_data):
        mp3_path = card_data["mp3"]
        correct_answer = card_data["answer"]

        # Check if the MP3 file exists
        if not os.path.exists(mp3_path):
            print(f"Warning: MP3 file not found: {mp3_path}")
            continue

        # Get the filename for the audio
        audio_filename = os.path.basename(mp3_path)

        # If there are duplicate filenames, rename them
        if audio_filename in [os.path.basename(f) for f in media_files]:
            base, ext = os.path.splitext(audio_filename)
            audio_filename = f"{base}_{idx}{ext}"
            # Create a temporary copy with the new name
            temp_path = os.path.join(os.path.dirname(mp3_path), audio_filename)
            shutil.copy2(mp3_path, temp_path)
            mp3_path = temp_path

        # Add to media files list
        media_files.append(mp3_path)

        # Create the audio HTML tag
        audio_html = f"[sound:{audio_filename}]"

        # Generate wrong options (4 random answers from other cards)
        other_answers = [ans for ans in all_answers if ans != correct_answer]

        # Make sure we have enough wrong answers
        if len(other_answers) < 4:
            print(
                f"Warning: Not enough unique answers for card {idx + 1}. Need at least 5 unique answers in the deck."
            )
            # Duplicate some answers if necessary
            while len(other_answers) < 4:
                other_answers.append(f"{random.choice(all_answers)} (variation)")

        # Select 4 random wrong answers
        wrong_options = random.sample(other_answers, 4)

        # Create all 5 options and shuffle them
        all_options = [correct_answer] + wrong_options
        random.shuffle(all_options)

        # Find the position of the correct answer (1-based index)
        correct_position = all_options.index(correct_answer) + 1

        # Create the note
        note = genanki.Note(
            model=audio_mc_model,
            fields=[
                audio_html,
                correct_answer,
                all_options[0],
                all_options[1],
                all_options[2],
                all_options[3],
                all_options[4],
                str(correct_position),
            ],
        )

        # Add note to deck
        deck.add_note(note)

    # Add media files to the package
    package.media_files = media_files

    # Write the package to a file
    package.write_to_file(output_filename)

    print(f"Successfully created Anki deck: {output_filename}")
    print(f"Total cards created: {len(deck.notes)}")

    # Clean up temporary files if any were created
    for media_file in media_files:
        if "_" in os.path.basename(media_file) and media_file != card_data["mp3"]:
            try:
                os.remove(media_file)
            except:
                pass

    return output_filename


# Example usage
if __name__ == "__main__":
    # Parse command line arguments. There should be one: the basename
    # of the input yaml, output apkg, and deck_name
    if len(sys.argv) != 2:
        print(
            "Usage: python create_flashcards.py [input, output, and deck title basename with no extension]"
        )
        sys.exit(1)

    # Make the filenames and title
    base = sys.argv[1]
    in_yaml_filename = os.path.join("input", f"{base}.yml")
    out_apkg_filename = os.path.join("output", f"{base}.apkg")
    deck_name = base.replace("_", " ").replace("-", " ").title()
    print(in_yaml_filename)
    print(out_apkg_filename)
    print(deck_name)

    # Create flashcard media and answers
    cards_data = create_flashcards(in_yaml_filename)

    # Create the deck
    saved_filename = create_audio_multiple_choice_deck(
        cards_data=cards_data,
        deck_name=deck_name,
        output_filename=out_apkg_filename,
    )

    print("Saved:", saved_filename)
