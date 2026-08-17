# Import OpenAI and supporting libraries
import os
from itertools import islice
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set. Add it to your .env file.")


def read_text_from_file(filename):
    """
    Reads the first 500 lines of content from a file and returns it as a string.
    Args: filename (str): The name of the file to read.
    Returns: str: The content of the file as a string, or an empty string if the file is not found.
    """
    try:
        with open(filename, 'r') as file:
            return ''.join(islice(file, 500))
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return ""

# Read content from the file
content = read_text_from_file("physics_lecture.txt")

# Set up the OpenAI client
client = OpenAI(api_key=API_KEY)

# Setting up the recommended model
model = "gpt-4o-mini"

# Define the system prompt (describing the assistant's behavior)
system_prompt = """
You are a teaching assistant that generates multiple-choice questions from a provided educational text.
Your role is to assist educators by creating quiz questions with one correct answer.
"""

# Define the user prompt template (input provided by the user)
user_prompt = """
Generate a multiple-choice quiz question from the given text:

Format:
Question: <Generated Question>
Options:
a) <Option 1>
b) <Option 2>
c) <Option 3>
d) <Option 4>
Answer: <Correct Option>
"""

def generate_quiz_questions(text):
    """
    Generates a list of multiple-choice quiz questions and answers from the provided text.
    Args: text (str): The input text from which quiz questions are generated.
    Returns: list: A list of dictionaries containing quiz questions, options, and correct answers.
    """
    # List to store generated quiz questions and answers
    quiz_data_list = []

    for i in range(5):
        
        # Get a response from the OpenAI API to generate the quiz questions
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt + text},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500
        )

        # Extract the questions and answers from the response
        question_and_answer = response.choices[0].message.content

        # Add the generated question and answer to the list
        quiz_data_list.append(question_and_answer)

    return quiz_data_list

# Generate quiz questions from the content provided
quiz_data = generate_quiz_questions(content)

# View the first question and answer set
quiz_data[0]