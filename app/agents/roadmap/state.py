from typing import List, Optional
from pydantic import BaseModel, Field

class StudyTask(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    topic: str

class TentativePhase(BaseModel):
    phase_name: str
    start_date: str
    end_date: str
    topics: List[str]

class TentativePhaseList(BaseModel):
    phases: List[TentativePhase]

class StudyTaskList(BaseModel):
    tasks : List[StudyTask]
    
class StudyPlanState(BaseModel):
    exam_name: str
    exam_date: str
    daily_hours: int
    syllabus: List[str]
    start_date: str
    tentative_plan: Optional[TentativePhaseList] | List[str] = []
    approved_phase: Optional[TentativePhaseList] | List[str] | List[TentativePhase]= []
    detailed_tasks: Optional[StudyTaskList] | List[str] = []