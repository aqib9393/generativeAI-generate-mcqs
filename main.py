import pdfplumber
import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def generate_mcqs(question):
    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 1024,
    }

    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config)

    prompt_parts = [f'''Generate 10 multiple-choice questions (MCQs) with four options based on the following content:\n\n{question}. Return the answer in the following format:\n
	Each question must have one correct answer and four answer options. \n
	Ensure that the questions cover various topics and concepts in the source material. \n
	Formatting: \n
	Each MCQ should be presented in the following format: \n
	Question: [Your question here] \n
	Options: \n
	A) [Option A] \n
	B) [Option B] \n
	C) [Option C] \n
	D) [Option D] \n
	Correct Answer: [Specify the correct answer] \n
.\nAnswer:''']

    response = model.generate_content(prompt_parts)
    
    return response.text

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def generate_mcqs_from_content(content):
    response = generate_mcqs(content)
    return response

def parse_mcqs(mcqs_text):
    mcqs = []
    questions = mcqs_text.split("Question:")
    
    for question in questions[1:]:  
        question_text = question.strip().split("\nOptions:")[0].strip()
        options_text = question.strip().split("Options:")[1].strip().split("\nCorrect Answer:")[0].strip()
        correct_answer = question.strip().split("Correct Answer:")[1].strip()
        
        options = options_text.split("\n")
        
        mcqs.append({
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer
        })
    
    return mcqs

def display_mcqs(mcqs):
    for idx, mcq in enumerate(mcqs):
        st.write(f"Q{idx + 1}: {mcq['question']}")
        st.write("Options:")
        st.markdown(f"""
            A) {mcq['options'][0]}  
            B) {mcq['options'][1]}  
            C) {mcq['options'][2]}  
            D) {mcq['options'][3]}
        """)
        st.markdown(f"**Correct Answer**: {mcq['correct_answer']}")

def main():
    st.set_page_config(page_title="MCQ Generator", layout="wide")
    
    st.title("MCQ Generator from PDF")

    pdf_file = st.file_uploader("Upload PDF", type="pdf")
    
    if pdf_file is not None:
        with st.spinner("Extracting text from the PDF..."):
            pdf_text = extract_text_from_pdf(pdf_file)
        
        st.write("PDF content extracted. Generating MCQs...")

        mcqs_text = generate_mcqs_from_content(pdf_text)

        st.subheader("Raw API Response")
        st.write(mcqs_text)  

        if mcqs_text:
            mcqs = parse_mcqs(mcqs_text)

            st.subheader("Generated MCQs:")
            display_mcqs(mcqs)
        else:
            st.write("No MCQs generated. Please check the API response.")

if __name__ == "__main__":
    main()
