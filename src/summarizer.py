import os
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from groq import Groq  # Ensure you have the correct Groq API client installed

# Set up Groq API key
os.environ["GROQ_API_KEY"] = "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"
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Update the PDF file path here
pdf_file_path = r'C:/Users/joshu/Downloads/segmentpaper.pdf'  # Change to your correct PDF path
pdfreader = PdfReader(pdf_file_path)
text = ''
for i, page in enumerate(pdfreader.pages):
    content = page.extract_text()
    if content:
        text += content

docs = [Document(page_content=text)]

# Function to summarize the text using Groq API
def summaryfunc(text):
    # Initial summary prompt
    template = '''Write a summary of the following text covering all the important points.
    The text: `{text}`
    '''

    initial_prompt = PromptTemplate(
        input_variables=['text'],
        template=template
    )

    # Text splitter for long documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=20)
    chunks = text_splitter.create_documents([text])

    # Final combination prompt with a fun title
    final_combine_prompt = '''Provide a final summary of the following text covering all the important points. 
    Sprinkle it with some jokes, and provide a funny and interesting title for the summary. 
    Put the title at the top. Don't mention that this is a summary from a text.
    text: `{text}`
    '''

    final_prompt = PromptTemplate(
        input_variables=['text'],
        template=final_combine_prompt
    )

    # Function to run inference via Groq API for each chunk
    def groq_summarize(chunk_text, prompt_template):
        prompt = prompt_template.format(text=chunk_text)
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a summarizer."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192"  # Use a model you have access to
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

# Example usage
if __name__ == "__main__":
    summary_output = summaryfunc(text)
    print(summary_output)
