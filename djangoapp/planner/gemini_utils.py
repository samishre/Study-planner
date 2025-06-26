import google.generativeai as genai
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

def gemini_generate_schedule(subject_name, exam_date, daily_hours, topics):
    try:
        today = datetime.now().date()
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
        study_days = (exam_dt - today).days
        if study_days <= 0:
            print("❌ Exam date is today or in the past")
            return None

        # Format topics with title and difficulty for prompt
        formatted_topics = "\n".join(
            f"- {topic['title']} (Difficulty: {topic['difficulty']})" for topic in topics
        )

        prompt = f"""
You are an expert study schedule planner. Create a balanced study plan.

Subject: '{subject_name}'
Exam Date: {exam_date}
Today's Date: {today.strftime('%Y-%m-%d')}
Days Left: {study_days}
Daily Study Hours: {daily_hours}

Topics (with difficulty level from 1 to 5):
{formatted_topics}

Output ONLY a valid JSON list in this format:
[
  {{"date": "YYYY-MM-DD", "topic": "Topic Title", "hours": 2}},
  ...
]
Respond with ONLY the JSON, no explanations or extra text.
"""

        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)

        print("Gemini raw response:", response.text)

        clean_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        print("Cleaned response:", clean_response)

        return json.loads(clean_response)

    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None
