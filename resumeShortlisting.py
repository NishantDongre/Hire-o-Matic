import os

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def convert_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n".join(p.extract_text() for p in reader.pages)


def preprocess(text, stop_words):
    tokens = word_tokenize(text.lower())
    clean_tokens = [token for token in tokens if token.isalpha()
                    and token not in stop_words]
    return ' '.join(clean_tokens)


def resumeShortlisting():
    # Only once download this nltk modules
    # nltk.download('stopwords')
    # nltk.download('punkt')

    all_resumes = []

    pdf_resume_path = 'pdfResume'
    pdf_files = os.listdir(pdf_resume_path)

    # Convert all the pdf files to txt format and then append it in all_resumes array
    for file_name in pdf_files:
        if file_name.endswith('.pdf'):
            file_path = os.path.join(pdf_resume_path, file_name)
            resume_text = convert_to_text(file_path)
            all_resumes.append(resume_text)

    # Preprocessing
    stop_words = set(stopwords.words('english'))

    #  Get the upload JD
    job_description = ""
    txt_jd_path = 'txtJD'

    for file_name in os.listdir(txt_jd_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(txt_jd_path, file_name)
        with open(file_path, 'r') as f:
            jd_text = f.read()
            job_description = jd_text

    job_description_clean = preprocess(job_description, stop_words)
    resumes_clean = [preprocess(resume, stop_words) for resume in all_resumes]

    # Feature extraction
    vectorizer = TfidfVectorizer()
    job_description_vector = vectorizer.fit_transform([job_description_clean])
    resumes_vectors = vectorizer.transform(resumes_clean)

    # Matching
    similarity_scores = cosine_similarity(
        job_description_vector, resumes_vectors)

    # Ranking
    ranked_resumes_indices = similarity_scores.argsort()[0][::-1]

    # Selection
    top_resumes = [all_resumes[i] for i in ranked_resumes_indices]

    # Print top ranked resumes
    return top_resumes
