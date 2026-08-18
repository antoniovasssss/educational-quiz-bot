# Educational Quiz Bot

This project reads a lecture text file, uses OpenAI to generate multiple-choice quiz questions, and runs an interactive quiz in the terminal.

## Setup

1. Install the dependencies:

	```powershell
	pip install -r requirements.txt
	```

2. Create a `.env` file in this folder with your OpenAI API key:

	```text
	OPENAI_API_KEY=your_api_key_here
	```

3. Make sure `physics_lecture.txt` is in the same folder as `main.py`.

## Run the quiz

```powershell
python main.py
```

The bot will generate five quiz questions from the lecture, ask for answers one at a time, explain each answer, and show a final score with topics to revise.

## What the bot does

- Generates all questions in one OpenAI request.
- Requests structured JSON instead of free-form text.
- Validates that each question has four options and one correct answer.
- Runs only when `main.py` is executed directly, so functions can be imported safely into a notebook.
- Loads `physics_lecture.txt` relative to `main.py`, which avoids notebook working-directory issues.