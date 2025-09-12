

# Node 1: Tentative plan
def generate_tentative_plan(state: StudyPlanState) -> StudyPlanState:

    tentative_llm = llm.with_structured_output(TentativePhaseList)

    prompt = [
        SystemMessage(content="You are a helpful exam roadmap assistant."),
        HumanMessage(content=TENTATIVE_ROADMAP_PROMPT.format(
            exam_name=state.exam_name,
            exam_date=state.exam_date,
            daily_hours=state.daily_hours,
            syllabus=state.syllabus,
            start_date=state.start_date
        ))
    ]
    response = tentative_llm.invoke(prompt)
    print(response)
    return merge_tentative(state, response)

# Node 2: Human approval
def wait_for_approval(state: StudyPlanState) -> StudyPlanState:

    approved = False
    while True:

        daily_hours = input('Enter daily time you can give for preparation in (hrs): ')
        if not daily_hours.isalpha() and 1 <= int(daily_hours) <= 24:
            break
        else:
            print('Input should be between 1 and 24')
    
    state.daily_hours = daily_hours
    while not approved:

        print("\n--- Tentative Plan ---")

        for idx, phase in enumerate(state.tentative_plan.phases):

   

            print(f"{idx+1}. {phase.phase_name} ({phase.start_date} → {phase.end_date}) Topics: {phase.topics}")
        choice = input("Select a to approve (or 'r' to regenerate): ")
        if choice.lower() == 'r':
            state = generate_tentative_plan(state)

        elif choice.lower() == 'a':
            idx = len(state.approved_phase)
            state.approved_phase.append(state.tentative_plan.phases[idx])
            approved = True
        else:
            print('Invalid input...')
    return state


# Node 3: Detailed 2-week plan
from datetime import datetime, timedelta
def generate_detailed_plan(state: StudyPlanState) -> StudyPlanState:
    start = datetime.strptime(state.approved_phase[-1].start_date, "%Y-%m-%d")
    # end = start + timedelta(days=13)
    sundays = [
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(14)
        if (start + timedelta(days=i)).weekday() == 6
    ]

    llm = ChatOpenAI(model = 'gpt-4o-mini', temperature = 0, max_completion_tokens=  5000)
    detailed_llm = llm.with_structured_output(StudyTaskList)

    prompt = [
        SystemMessage(content="You are a detailed study schedule generator."),
        HumanMessage(content=DETAILED_2W_PLAN_PROMPT.format(
            exam_name=state.exam_name,
            exam_date=state.exam_date,
            daily_hours=state.daily_hours,
            phase_name=state.approved_phase[-1].phase_name,
            phase_start=state.approved_phase[-1].start_date,
            phase_end=state.approved_phase[-1].end_date,
            syllabus_for_phase=state.approved_phase[-1].topics,
            sundays=sundays
        ))
    ]

    response = detailed_llm.invoke(prompt)
    print(prompt)
    return merge_detailed(state, response)