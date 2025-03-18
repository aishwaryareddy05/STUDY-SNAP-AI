import os
from groq import Groq  # Ensure you have the correct Groq API client installed
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Set up Groq API key
os.environ["GROQ_API_KEY"] = "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"
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY environment variable is not set.")

# Initialize Groq client
client = Groq(api_key=api_key)

# Prompt template for providing study materials
template = """
You are an educational assistant. Given the topic "{topic}", please provide study materials including YouTube video links, research paper links, and online article links to assist the student in further studies.
### RESPONSE_JSON
{response_json}
"""
study_materials_prompt = PromptTemplate(
    input_variables=["topic", "response_json"],
    template=template,
)

# Function to generate study materials using Groq API
def provide_study_materials(topic):
    prompt = study_materials_prompt.format(
        topic=topic,
        response_json=None  # Placeholder for JSON data (not used)
    )

    try:
        # Use Groq client for optimized inference (Groq hardware)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an educational assistant."},
                {"role": "user", "content": prompt},
            ],
            model="llama3-8b-8192"  # Use a model you have access to
        )
        
        generated_text = response.choices[0].message.content
        return generated_text
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage:
if __name__ == "__main__":
    topic = input("Enter topic you'd like materials on: ")

    study_materials = provide_study_materials(topic)
    print(study_materials)
