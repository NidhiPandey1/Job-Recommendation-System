import streamlit as st
import pandas as pd
import pickle
import os

# Assuming userprofile_df and job_df are already defined DataFrames
# Replace this with your actual DataFrames or loading logic
userprofile_df = pd.read_csv('userprofile.csv')
job_df = pd.read_csv('job_data.csv')

# Function to load data from pickle file
@st.cache_data()
def load_data(pickle_file):
    try:
        with open(pickle_file, 'rb') as file:
            data = pickle.load(file)
            if isinstance(data, dict) and 'userprofile_df' in data and 'job_df' in data:
                return data['userprofile_df'], data['job_df']
            else:
                raise ValueError("Invalid pickle file format. Expected a dictionary with 'userprofile_df' and 'job_df'.")
    except FileNotFoundError:
        st.error(f"File {pickle_file} not found.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return None, None

# Define recommend_jobs function
def recommend_jobs(applicantId_or_skill, userprofile_df, job_df, top_n=3):
    if isinstance(applicantId_or_skill, str):  # Applicant ID case
        user_row = userprofile_df[userprofile_df['applicantId'] == applicantId_or_skill]

        if user_row.empty:
            return None  # Return None if applicant ID not found

        user_skills = set(user_row['skills'].iloc[0].lower().split(','))

        recommended_jobs = []
        for idx, job_data in job_df.iterrows():
            job_skills = set(job_data['skills'].lower().split(','))

            if user_skills.intersection(job_skills):
                recommended_jobs.append({
                    'position': job_data['position'],
                    'location': job_data['location'],
                    'skills': job_data['skills'],
                    'vacancies': job_data['vacancies'],
                    'minExp': job_data['minExp']
                })
                if len(recommended_jobs) == top_n:
                    break

    elif isinstance(applicantId_or_skill, list):  # Skills case
        recommended_jobs = []
        for skill in applicantId_or_skill:
            skill = skill.strip().lower()
            for idx, job_data in job_df.iterrows():
                job_skills = set(job_data['skills'].lower().split(','))

                if skill in job_skills:
                    recommended_jobs.append({
                        'position': job_data['position'],
                        'location': job_data['location'],
                        'skills': job_data['skills'],
                        'vacancies': job_data['vacancies'],
                        'minExp': job_data['minExp']
                    })
                    if len(recommended_jobs) == top_n:
                        break

    return recommended_jobs

# Main Streamlit app
def main():
    # Set page config
    st.set_page_config(page_title="Job Recommendation Engine", page_icon=":briefcase:", layout="wide", initial_sidebar_state="expanded")

    # Title
    st.title("Job Recommendation Engine")
    
    background_image = "image.jpg"

    # Set the app's background style
    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background: url("{background_image}");
            background-size: cover;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
      
    # Customizing the app appearance
    page_bg_color = "#f0f5f5"  # Light blue-gray background
    st.markdown(f"""<style>
        .reportview-container {{
            background-color: {page_bg_color};
        }}
        </style>
    """, unsafe_allow_html=True)


    # Extract unique skills from job_df
    unique_skills = set()
    for skills_str in job_df['skills']:
        skills_list = [skill.strip().lower() for skill in skills_str.split(',')]
        unique_skills.update(skills_list)
    unique_skills = sorted(unique_skills)  # Sort skills alphabetically

    # Input fields
    option = st.selectbox("Select an option:", ["Applicant ID", "Skills"])

    if option == "Applicant ID":
        applicant_id_options = list(userprofile_df['applicantId'])
        applicant_id = st.selectbox("Select Applicant ID:", applicant_id_options)
        if st.button("Recommend Jobs"):
            if not applicant_id:
                st.warning("Please select an Applicant ID.")
            else:
                recommended_jobs = recommend_jobs(applicant_id, userprofile_df, job_df)
                if recommended_jobs:
                    st.header(f"Recommended Jobs for Applicant ID {applicant_id}:")
                    for job in recommended_jobs:
                        if job['position'].lower() == 'data analyst':
                            st.markdown(f"### <span style='color:green'>{job['position']}</span>", unsafe_allow_html=True)
                        else:
                            st.subheader(job['position'])
                        st.write(f"Location: {job['location']}")
                        st.write(f"Skills Required: {job['skills']}")
                        st.write(f"Vacancies: {job['vacancies']}")
                        st.write(f"Minimum Experience Required: {job['minExp']}")
                        st.write("---")
                else:
                    st.warning(f"No matching jobs found for Applicant ID {applicant_id}.")

    elif option == "Skills":
        selected_skills = st.multiselect("Select Skills:", unique_skills)
        if st.button("Recommend Jobs"):
            if not selected_skills:
                st.warning("Please select at least one skill.")
            else:
                recommended_jobs = recommend_jobs(selected_skills, userprofile_df, job_df)
                if recommended_jobs:
                    st.header(f"Recommended Jobs based on Skills:")
                    for job in recommended_jobs:
                        if job['position'].lower() == 'data analyst':
                            st.markdown(f"### <span style='color:green'>{job['position']}</span>", unsafe_allow_html=True)
                        else:
                            st.subheader(job['position'])
                        st.write(f"Location: {job['location']}")
                        st.write(f"Skills Required: {job['skills']}")
                        st.write(f"Vacancies: {job['vacancies']}")
                        st.write(f"Minimum Experience Required: {job['minExp']}")
                        st.write("---")
                else:
                    st.warning(f"No matching jobs found based on selected skills.")

if __name__ == "__main__":
    main()
