from langchain.prompts import PromptTemplate



# TENTATIVE ROADMAP FOR EXAM

TENTATIVE_ROADMAP_PROMPT = PromptTemplate(
    input_variables=["exam_name", "exam_date", "daily_hours", "syllabus", "start_date"],
    template="""
You are an expert exam planner. Create a tentative high-level study roadmap.

Exam: {exam_name}
Exam Date: {exam_date}
Daily Study Hours: {daily_hours}
Syllabus: {syllabus}
Start Date: {start_date}

Rules:
1. Divide the syllabus into balanced phases from start date until the exam date.
2. Each phase should have:
   - phase_name
   - start_date
   - end_date
   - topics (list)
3. Sundays should be used for "Weekly Revision" — mention them in description if relevant.
4. Output only valid JSON:
[
  {{
    "phase_name": "...",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "topics": ["topic1", "topic2"]
  }}
]
"""
)

# DETAILED ROADMAP FOR NEXT 2 WEEKS

DETAILED_2W_PLAN_PROMPT = PromptTemplate(
    input_variables=["exam_name", "exam_date", "daily_hours", "phase_name", "phase_start", "phase_end", "syllabus_for_phase", "sundays"],
    template="""
You are a study plan generator.

Exam: {exam_name} ({exam_date})
Phase: {phase_name} ({phase_start} → {phase_end})
Daily Study Hours: {daily_hours}
Syllabus topics for this phase: {syllabus_for_phase}
Sundays in range: {sundays}

Rules:
1. Create tasks for each date between phase_start and phase_end (2 weeks only).
2. On Sundays, set topic to "Weekly Revision".
3. Each non-Sunday must have study tasks totalling {daily_hours} hours.
4. Output only valid JSON:
[
  {{
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "end_time": "HH:MM",
    "topic": "..."
  }}
]
"""
)
