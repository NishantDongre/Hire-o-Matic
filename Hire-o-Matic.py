import base64
import json
import os
import time

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from streamlit_option_menu import option_menu

from functionality import (evaluate_candidate_by_comments,
                           interviewQuestionPrompt,
                           shortlisting_top_3_candidate)

# Load the API KEYS
load_dotenv()


def convert_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(p.extract_text() for p in reader.pages)


def read_file(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
    return file_contents


def convert_pdf_folder_to_txt(pdf_path):
    """Converts all PDF files in a folder to TXT files, preserving their names."""

    for filename in os.listdir(pdf_path):
        if filename.endswith('.pdf'):
            individual_pdf_path = pdf_path + "/" + filename
            # filename is Resume_1.pdf
            st.write(individual_pdf_path)
            txt_path = '/txtResume/' + \
                filename.rsplit(".", 1)[0]  # Preserve base name
            st.write(txt_path)
            try:
                text = convert_to_text(pdf_path)
            except Exception as e:
                print(f"Error converting '{filename}': {e}")


# Initialization the key -> run_interviewQuestionTab
if 'run_interviewQuestionTab' not in st.session_state:
    st.session_state['run_interviewQuestionTab'] = True


def main():
    st.set_page_config(layout="centered")
    # Remove the default menu
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # Remove whitespace from the top of the page and sidebar
    st.markdown("""
            <style>
                .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                    }
                .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                    }
            </style>
            """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
        </style>
        """, unsafe_allow_html=True)

    # Navbar
    st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)
    st.markdown("""
            <style>
            .stApp header {
                z-index: 1;       
            }
            </style>
        """, unsafe_allow_html=True)

    # CSS for Navbar at top with full width
    st.markdown("""
            <style>
            .st-d4.st-b8.st-d5 {
            width: 30%;
            }
            .navbar {
            position: fixed;
            top: 0px;
            left: 0px;
            width: 96%;
            padding: 0px;
            z-index: 2;
            padding-left: 20px;
            padding-right: 39px;
            background: transparent;
            }
            .navbar img {
                width: 70px;
                height: 50px;  
            }
            .navbar-brand img {
            max-height: 45px !important;
            }
            [data-testid="stHeader"] {{
            z-index: 0;
            background: rgba(0,0,0,0);
            }}
            </style>
            """,
                unsafe_allow_html=True
                )

    st.markdown(f"""
        <style>
            .navbar {{
                padding-right: 10px;
                padding-left: 30px;
                background-color:#1a2733;
                width: 100%;
                height: 3.75rem;
                background-image: linear-gradient(to bottom right, transparent 50%, rgb(0, 112, 242) 125%);
                border-bottom: solid 0.25rem rgb(0, 112, 242);
            }}
            .navbar-brand  {{
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 1.4rem;
            }}
        </style>
        <div>
            <nav class="navbar">
                <div class="navbar-brand" >
                    Hire-o-Matic
                </div>
            </nav>
        </div>
        """, unsafe_allow_html=True)

    # horizontal menu
    option_selected = option_menu(None, ["Resume Shortlisting", "Evaluate Companion"],
                                  icons=['clipboard', 'file-earmark-check'],
                                  menu_icon="cast", default_index=0, orientation="horizontal")

    # Gemini model
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel('gemini-pro')

    if option_selected == "Resume Shortlisting":
        # Upload the Jd
        txt_jd_path = 'txtJD'
        upload_txt_jd = st.file_uploader(
            "Upload Job Description", accept_multiple_files=False, type='txt')

        if upload_txt_jd:
            st.toast("JD uploaded")
            with st.spinner('Uploading JD...'):
                # Removing all the jd txt files in the "txtJD" folder
                # Get a list of all files in the folder
                files = os.listdir(txt_jd_path)

                # Iterate over each file and delete it
                for file_name in files:
                    file_path = os.path.join(txt_jd_path, file_name)
                    os.remove(file_path)

                # Uploaded the txt files
                with open(os.path.join("txtJD/") + 'jd.txt', "wb") as f:
                    f.write(upload_txt_jd.getbuffer())

        pdf_resume_path = 'pdfResume'
        uploaded_pdf_resumes = st.file_uploader(
            "Upload Resumes", accept_multiple_files=True)

        if uploaded_pdf_resumes:
            with st.spinner('Uploading Resumes...'):
                # Removimg all the resume pdf files in the "pdfResume" folder
                # Get a list of all files in the folder
                files = os.listdir(pdf_resume_path)

                # Iterate over each file and delete it
                for file_name in files:
                    file_path = os.path.join(pdf_resume_path, file_name)
                    os.remove(file_path)

                # Uploaded the txt files
                for textfile in uploaded_pdf_resumes:
                    # st.warning(textfile.name)
                    with open(os.path.join("pdfResume/") + textfile.name, "wb") as f:
                        f.write(textfile.getbuffer())

                # convert pdf Resume to txt files
                txt_resume_path = 'txtResume'
                files = os.listdir(txt_resume_path)

                # Iterate over each file and delete it
                for file_name in files:
                    file_path = os.path.join(txt_resume_path, file_name)
                    os.remove(file_path)

            st.toast("Resumes uploaded")
        shortlisting_btn = st.button("Analyze")

        # For White space only when we are not analysing the resumes
        if not shortlisting_btn:
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(" ")

        if shortlisting_btn:
            with st.spinner('Analysing Resumes...'):
                prompt = shortlisting_top_3_candidate()
                response = model.generate_content(prompt)

                # toast
                st.toast("Success")
                st.write(response.text)

    else:
        st.header("Upload Resume to Generate questions")

        def displayPDF(file):
            # Opening file from file path
            with open(file, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')

            # Embedding PDF in HTML
            pdf_display = F'<embed src="data:application/pdf;base64,{
                base64_pdf}" width="580" height="800" type="application/pdf">'

            # Displaying File
            st.markdown(pdf_display, unsafe_allow_html=True)

        # Path
        upload_resume_pdf_path = 'uploadedResume/'
        jd_path = "txtJD/jd.txt"

        # content
        resume_content = ""
        jd_content = read_file(jd_path)

        uploaded_files = st.file_uploader(
            "Upload Resume here", accept_multiple_files=False, type='pdf')

        if uploaded_files:
            with st.spinner('Uploading PDF...'):
                # Removing all the pdf files in the "uploadedResume" folder
                # Get a list of all files in the folder
                files = os.listdir(upload_resume_pdf_path)

                # Iterate over each file and delete it
                for file_name in files:
                    file_path = os.path.join(upload_resume_pdf_path, file_name)
                    os.remove(file_path)

                # Uploaded the pdf file
                with open(os.path.join("uploadedResume/", "resume.pdf"), "wb") as f:
                    f.write(uploaded_files.getbuffer())

                resume_content = convert_to_text(
                    upload_resume_pdf_path + "resume.pdf")
                displayPDF(upload_resume_pdf_path + "resume.pdf")

        # Variable for Candidate Interview Comments by Interviewer
        textBoxInterviewComment = ''

        interviewQuestionTab, evaluateCandidateTab, improveCommentsTab = st.tabs(
            ["✨ Generate Questions", "🎯 Evalute Candidate", "📝 Improve the Comments"])
        # 📈 🗃

        with interviewQuestionTab:
            if resume_content and st.session_state['run_interviewQuestionTab'] == True:
                st.session_state['run_interviewQuestionTab'] = False
                with st.spinner('Generating Questions...'):
                    prompt = interviewQuestionPrompt(
                        resume_content, jd_content)
                    response = model.generate_content(prompt)
                    st.toast("Successfully generated questions")
                    st.write(response.text)
            else:
                st.info("Please upload Resume")

        with evaluateCandidateTab:
            if resume_content:
                with st.spinner('Evaluating Comments...'):
                    textBoxInterviewComment = st.text_area(
                        'Write down your comments here', "")
                    # Comments should be atleast of 50 words
                    if len(textBoxInterviewComment) > 50:
                        prompt = evaluate_candidate_by_comments(
                            1, "EVAL", resume_content, textBoxInterviewComment)
                        response = model.generate_content(prompt)
                        st.toast("Successfully Evaluated the candidate")
                        st.write(response.text)
            else:
                st.info("Please upload Resume")

        with improveCommentsTab:
            if resume_content:
                with st.spinner('Improving Comments...'):
                    prompt = evaluate_candidate_by_comments(
                        1, "IMPROVE", resume_content, textBoxInterviewComment)
                    response = model.generate_content(prompt)
                    st.write(response.text)
            else:
                st.info("Please upload Resume")


if __name__ == '__main__':
    main()
