# phase_dates.py
from datetime import date, timedelta

def calculate_phases_with_sundays(exam_date_str, start_date_str=None):
    exam_date = date.fromisoformat(exam_date_str)
    start_date = date.fromisoformat(start_date_str) if start_date_str else date.today() + timedelta(days=1)
    
    total_days = (exam_date - start_date).days + 1
    
    # Phase distribution ratios
    phase_ratios = [0.5, 0.25, 0.15, 0.10]  # learning, rev1, rev2, final prep
    phase_lengths = [int(total_days * r) for r in phase_ratios]
    
    # Adjust for rounding
    diff = total_days - sum(phase_lengths)
    if diff != 0:
        phase_lengths[0] += diff
    
    phases = []
    current_start = start_date
    phase_names = ["Phase 1: Learning", "Phase 2: Revision 1", "Phase 3: Revision 2", "Phase 4: Final Prep & Mock Tests"]
    
    # Generate phase ranges
    for name, length in zip(phase_names, phase_lengths):
        phase_end = current_start + timedelta(days=length - 1)
        phases.append({
            "name": name,
            "start_date": current_start.isoformat(),
            "end_date": phase_end.isoformat()
        })
        current_start = phase_end + timedelta(days=1)
    
    # Find all Sundays in the range
    sundays = []
    current_day = start_date
    while current_day <= exam_date:
        if current_day.weekday() == 6:  # Sunday
            sundays.append(current_day.isoformat())
        current_day += timedelta(days=1)
    
    return {
        "start_date": start_date.isoformat(),
        "exam_date": exam_date_str,
        "total_days": total_days,
        "phases": phases,
        "sundays": sundays
    }
