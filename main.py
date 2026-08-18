import json
import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"
DEFAULT_LECTURE_FILE = "physics_lecture.txt"
DEFAULT_QUESTION_COUNT = 5


SYSTEM_PROMPT = """
You are a teaching assistant that creates clear, accurate multiple-choice quiz questions from educational text.
Use only facts from the supplied lecture text. Create plausible distractors, but ensure exactly one answer is correct.
Return valid JSON only.
"""


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set. Add it to your .env file.")

    return OpenAI(api_key=api_key)


def read_text_from_file(filename):
    """Read lecture text from a file next to this script."""
    lecture_path = Path(__file__).resolve().with_name(filename)

    try:
        content = lecture_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"Error: {lecture_path.name} was not found next to main.py.") from None

    if not content.strip():
        raise SystemExit(f"Error: {lecture_path.name} is empty.")

    return content


def build_user_prompt(text, question_count, difficulty):
    return f"""
Generate {question_count} multiple-choice quiz questions from the lecture text below.

Rules:
- Difficulty: {difficulty}
- Cover different parts of the lecture where possible.
- Each question must have exactly four options.
- `answer_index` must be 0, 1, 2, or 3.
- Include a short explanation for the correct answer.
- Return JSON in exactly this shape:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer_index": 0,
      "explanation": "Why the answer is correct",
      "topic": "Lecture topic",
      "difficulty": "{difficulty}"
    }}
  ]
}}

Lecture text:
{text}
"""


def generate_quiz_questions(text, question_count=DEFAULT_QUESTION_COUNT, difficulty="medium"):
    client = get_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(text, question_count, difficulty)},
        ],
        response_format={"type": "json_object"},
        max_tokens=1500,
    )

    content = response.choices[0].message.content
    quiz_data = json.loads(content)
    return validate_quiz(quiz_data, question_count)


def validate_quiz(quiz_data, expected_count):
    questions = quiz_data.get("questions")

    if not isinstance(questions, list) or not questions:
        raise ValueError("The model did not return a questions list.")

    validated_questions = []

    for index, question in enumerate(questions[:expected_count], start=1):
        options = question.get("options")
        answer_index = question.get("answer_index")

        if not question.get("question"):
            raise ValueError(f"Question {index} is missing question text.")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError(f"Question {index} must have exactly four options.")
        if answer_index not in range(4):
            raise ValueError(f"Question {index} has an invalid answer index.")

        validated_questions.append(
            {
                "question": question["question"],
                "options": options,
                "answer_index": answer_index,
                "explanation": question.get("explanation", "No explanation provided."),
                "topic": question.get("topic", "General"),
                "difficulty": question.get("difficulty", "medium"),
            }
        )

    return validated_questions


def ask_for_answer():
    answer_map = {"a": 0, "b": 1, "c": 2, "d": 3}

    while True:
        answer = input("Your answer (a/b/c/d): ").strip().lower()

        if answer in answer_map:
            return answer_map[answer]

        print("Please enter a, b, c, or d.")


def run_quiz(questions):
    score = 0
    missed_topics = []
    option_labels = ["a", "b", "c", "d"]

    for question_number, question in enumerate(questions, start=1):
        print(f"\nQuestion {question_number}: {question['question']}")

        for option_label, option in zip(option_labels, question["options"]):
            print(f"{option_label}) {option}")

        selected_index = ask_for_answer()
        correct_index = question["answer_index"]

        if selected_index == correct_index:
            score += 1
            print("Correct.")
        else:
            missed_topics.append(question["topic"])
            print(f"Incorrect. The correct answer was {option_labels[correct_index]}.")

        print(f"Explanation: {question['explanation']}")

    print(f"\nFinal score: {score}/{len(questions)}")

    if missed_topics:
        print("Topics to revise: " + ", ".join(sorted(set(missed_topics))))


def main():
    lecture_text = read_text_from_file(DEFAULT_LECTURE_FILE)
    questions = generate_quiz_questions(lecture_text)
    run_quiz(questions)


if __name__ == "__main__":
    main()