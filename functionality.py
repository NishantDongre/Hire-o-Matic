import json
import os

from resumeShortlisting import resumeShortlisting


def read_file(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
    return file_contents


def shortlisting_top_3_candidate():
    # Shortlisting candidate using NLP
    top_resume = resumeShortlisting()
    # Considering only top 8 candidates
    top_8_resume = top_resume[:8]

    prompt = """
    Please analyze the attached resumes in conjunction with the provided job description and 
    rank the top three resumes that best align with the requirements outlined in the job description. 
    Consider factors such as relevant skills, experience, education, and achievements mentioned 
    in the resumes, ensuring they closely match the job role's expectations. 

    Give me the name of the candidate and the skill that matches and the reason why we should interview that candidate.
    Also give text output in proper format with bold heading and proper struture should be there in your response.
    """
    prompt += "\n \n \n"
    prompt += "Job Description: \n \n" + read_file('txtJD/jd.txt')
    prompt += "\n \n \n"
    prompt += "All Resume are in Array format is: "
    prompt += "\n \n \n"
    prompt += json.dumps(top_8_resume)

    return prompt


def interviewQuestionPrompt(resume_content, jd_content):
    prompt = ("""
        You are conducting an interview for a software engineering position. 
        I have provided their resume and the job description for the position they are applying for. 
        Generate 10 interview questions tailored to assess the candidate's skills and experience. 
        Ensure that 7 questions are related to programming languages and technologies mentioned in the job description, and 3 questions are general to evaluate other skills and competencies.
        The questions should vary in difficulty to comprehensively evaluate the candidate's suitability for the position.
    """)
    prompt += ("\n \n")
    prompt += ("Below is the Resume of the Candidate: \n \n" + resume_content)
    prompt += ("\n \n")
    prompt += ("Below is the Job description: \n \n" + jd_content)
    prompt += ("""
       Additionally, include example responses for each question that are general and not personalized to any specific candidate's background. Highlight the important parts of both the questions and answers for better understanding.
    """)

    return prompt


def evaluate_candidate_by_comments(candidate, task, resume_content, textBoxInterviewComment):
    """
    Evaluates candidate's performance in the interview by the comments submitted
    by the interviewer.
    """
    return evaluate_comments_using_llm(textBoxInterviewComment, resume_content, task)


def evaluate_comments_using_llm(comments, resume_content, task):
    """
    Generates an evaluation of the candidates using the comments submitted
    by the interviewer.
    """
    resume_prompt = "Candidate's resume:\n"
    comments_prompt = "\n\nComments submitted by the interviewer:\n\n\n"
    if task == "EVAL":
        prompt = ("\n\n Based on the comments submitted by the interviewer, evaluate "
                  "the candidate's performance on these 5 parameters on scale of 5 and Score: 4/5 or (score Obtained)/5 . Also highlight the important parts:\n"
                  "Also give reason for giving that score and elaborate more for next Interviewer:"
                  "1. Problem solving and analytical skills"
                  "2. Design/architecture"
                  "3. Communication"
                  "4. Programming Language"
                  "5. Work Experience")
    else:
        prompt = ("\n\n Based on the feedback provided by the interviewer, rewrite the comments on the following five parameters while maintaining 'technical accuracy'. Elaborate on each point to offer valuable insights for the next interviewer conducting the subsequent round of the candidate's evaluation. Highlight critical sections: \n \n"
                  "1. Problem solving and analytical skills"
                  "2. Design/architecture"
                  "3. Communication"
                  "4. Programming Language"
                  "5. Work Experience")

    prompt += (comments_prompt + comments) + "\n \n \n"
    if task == 'EVAL':
        prompt += (resume_prompt + resume_content) + "\n \n \n"

    return prompt
