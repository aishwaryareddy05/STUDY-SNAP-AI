import os
import PyPDF2
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from groq import Groq

# Set up Groq API key
os.environ["GROQ_API_KEY"] = "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" # Replace with your actual API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Prompt template for generating MCQs
quiz_generation_template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to create a quiz of {number} multiple choice questions with difficulty {grade} out of 10 in {tone} tone.
Make sure questions are not repeated, conform to the text, and are structured as a hard entrance exam.
Make one third easy, one third medium, and one third hard questions.
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "grade", "tone"],
    template=quiz_generation_template,
)

# Function to generate multiple-choice questions using Groq API
def generate_questions(text, number, grade, tone):
    prompt = quiz_generation_prompt.format(text=text, number=number, grade=grade, tone=tone)
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are an MCQ generator."},
                      {"role": "user", "content": prompt}],
            model="llama3-8b-8192"
        )
        generated_text = response.choices[0].message.content
        return generated_text
    except Exception as e:
        return f"An error occurred: {e}"

# Function to parse a PDF file and extract text
def parse_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# Function to summarize the text using Groq API
def summaryfunc(text):
    initial_summary_template = '''Write a summary of the following text covering all the important points.
    The text: `{text}`'''
    
    initial_prompt = PromptTemplate(input_variables=['text'], template=initial_summary_template)

    # Text splitter for long documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)
    chunks = text_splitter.create_documents([text])

    final_summary_template = '''Provide a final summary of the following text covering all the important points. 
    Sprinkle it with some jokes, and provide a funny and interesting title for the summary. 
    Put the title at the top. Don't mention that this is a summary from a text.
    text: `{text}`'''
    
    final_prompt = PromptTemplate(input_variables=['text'], template=final_summary_template)

    def groq_summarize(chunk_text, prompt_template):
        prompt = prompt_template.format(text=chunk_text)
        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are a summarizer."},
                          {"role": "user", "content": prompt}],
                model="llama3-8b-8192"
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {e}"

    # Summarize each chunk
    summarized_chunks = [groq_summarize(chunk.page_content, initial_prompt) for chunk in chunks]

    # Combine all chunks into a final summary with a title
    final_summary_text = "\n".join(summarized_chunks)
    final_summary = groq_summarize(final_summary_text, final_prompt)

    return final_summary

# Prompt template for providing study materials
study_materials_template = """
You are an educational assistant. Given the topic "{topic}", please provide study materials including YouTube video links, research paper links, and online article links to assist the student in further studies.
### RESPONSE_JSON
{response_json}
"""
study_materials_prompt = PromptTemplate(
    input_variables=["topic", "response_json"],
    template=study_materials_template,
)

# Function to generate study materials using Groq API
def provide_study_materials(topic):
    prompt = study_materials_prompt.format(topic=topic, response_json=None)

    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are an educational assistant."},
                      {"role": "user", "content": prompt}],
            model="llama3-8b-8192"
        )
        
        generated_text = response.choices[0].message.content
        return generated_text
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit app layout
col1, col2 = st.columns([6, 1])

with col1:
        st.title("Study Snap 🤖 ")
        st.subheader(" - Your Smart AI-Powered Study Assistant")
  

with col2:
    st.image("robot-assistant.png", width=100)  

# File uploader
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if pdf_file is not None:
    text = parse_pdf(pdf_file)
    
    if "Error" in text:
        st.error(text)
    else:
        # Dropdown menu for navigating features
        st.header("Select an option:")
        option = st.selectbox("Choose an action:", ["Generate MCQs", "Summarize Content", "Provide Study Materials"])

        if option == "Generate MCQs":
            st.subheader("Generate Multiple Choice Questions")
            number_of_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
            grade_level = st.slider("Grade Level", min_value=1, max_value=10, value=5)
            quiz_tone = st.selectbox("Tone", ["curious", "serious", "funny"])

            if st.button("Generate MCQs"):
                questions = generate_questions(text, number_of_questions, grade_level, quiz_tone)
                st.subheader("Generated Multiple Choice Questions:")
                st.write(questions)

        elif option == "Summarize Content":
            st.subheader("Summarize PDF Content")
            if st.button("Generate Summary"):
                summary_output = summaryfunc(text)
                st.subheader("Summary:")
                st.write(summary_output)

        elif option == "Provide Study Materials":
            st.subheader("Provide Study Materials")
            topic = st.text_input("Enter topic you'd like materials on:")
            if st.button("Get Study Materials"):
                if topic:
                    study_materials = provide_study_materials(topic)
                    st.subheader("Study Materials:")
                    st.write(study_materials)
                else:
                    st.error("Please enter a topic.")
