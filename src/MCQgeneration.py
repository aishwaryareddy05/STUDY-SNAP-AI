import os
import PyPDF2
from langchain.prompts import PromptTemplate
from groq import Groq  # Ensure you have the correct Groq API client installed

# Set up API keys for Groq
os.environ["GROQ_API_KEY"] = "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"
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Prompt template for generating MCQs
template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to\
create a quiz of {number} multiple choice questions with difficulty {grade} out of 10 in {tone} tone.
Make sure questions are not repeated, conform to the text, and are structured as a hard entrance exam.
Make one third easy, one third medium, and one third hard questions.
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "grade", "tone"],
    template=template,
)

# Function to generate multiple-choice questions using Groq API
def generate_questions(text, number, grade, tone):
    # Build the prompt with context and format using the template
    prompt = quiz_generation_prompt.format(
        text=text,
        number=number,
        grade=grade,
        tone=tone
    )
    
    # Use Groq client for optimized inference (Groq hardware)
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an MCQ generator."},
                {"role": "user", "content": prompt},
            ],
            model="llama3-8b-8192"
        )
        generated_text = response.choices[0].message.content
        return generated_text
    except Exception as e:
        return f"An error occurred: {e}"

# Function to parse a PDF file and extract text
def parse_pdf(file_path):
    try:
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# Function to generate MCQs from a PDF file
def generate_questions_from_pdf(pdf_file_path, number, grade, tone):
    try:
        # Parse the text from the PDF
        text = parse_pdf(pdf_file_path)
        
        # Generate the questions using the parsed text
        quiz = generate_questions(text, number, grade, tone)
        return quiz
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    pdf_file_path = r"C:\Users\joshu\Downloads\segmentpaper.pdf" # Path to your PDF
    number_of_questions = 6
    grade_level = 7
    quiz_tone = "curious"

    # Generate MCQs from the PDF
    questions = generate_questions_from_pdf(pdf_file_path, number_of_questions, grade_level, quiz_tone)
    print(questions)
