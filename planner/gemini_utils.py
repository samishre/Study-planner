import google.generativeai as genai
import json
import re
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

        topic_titles = [topic['title'] for topic in topics]
        formatted_topics = "\n".join(
            f"- {topic['title']} (Difficulty: {topic['difficulty']})" for topic in topics
        )

        prompt = f"""
You are an expert study planner. Create a detailed study schedule from today to the exam date.

🔒 Rules:
- Only use the exact topics provided below. DO NOT invent, combine, or change them.
- Each topic has a difficulty level from 1 (easy) to 5 (hard).
- User has exactly {daily_hours} study hours per day.
-⛔️ The total duration of all sessions per day must NOT exceed {daily_hours} hours.
- You can divide the daily time into multiple sessions (1–3).
- Allocate **more time to harder topics**.
- Include 15-minute breaks between sessions.
- Each session should include: date, topic title, start_time, end_time (24hr, HH:MM).
- All study sessions must start exactly at 08:00 every day.
- Do NOT vary start times across days.


📌 Example Output Format:
[
  {{
    "date": "2025-06-28",
    "topic": "Photosynthesis",
    "start_time": "08:00",
    "end_time": "09:30"
  }},
  ...
]

Subject: '{subject_name}'
Exam Date: {exam_date}
Today's Date: {today.strftime('%Y-%m-%d')}
Total Study Days: {study_days}
Daily Study Limit: {daily_hours} hours

Here are the topics with difficulty level:
{formatted_topics}

Return only valid JSON (array of dictionaries). DO NOT wrap it in markdown or include explanations. Do not write anything outside the list.
"""

        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)

        if not response.text.strip():
            print("❌ Gemini returned empty response.")
            return None

        print("✅ Gemini raw response:", response.text)

        clean_response = (
            response.text.strip()
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        clean_response = re.sub(r",\s*(\])", r"\1", clean_response)

        print("✅ Cleaned response:", clean_response)

        schedule_data = json.loads(clean_response)

        if not isinstance(schedule_data, list):
            print("❌ Gemini response is not a list")
            return None

        print("✅ Parsed schedule data:", schedule_data)
        return schedule_data

    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print("🔍 Problematic response:", clean_response)
        return None
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return None
