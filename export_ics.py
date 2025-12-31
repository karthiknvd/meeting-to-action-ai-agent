from ics import Calendar, Event
from datetime import datetime, timedelta
import dateparser  # install this: pip install dateparser


def parse_deadline(deadline_text):
    """
    Converts natural language like 'Friday' or 'next week' into a real datetime.
    """
    if not deadline_text:
        return datetime.now() + timedelta(days=1)

    parsed_date = dateparser.parse(deadline_text, settings={'PREFER_DATES_FROM': 'future'})
    if parsed_date:
        return parsed_date
    else:
        # fallback to 2 days from now if parsing fails
        return datetime.now() + timedelta(days=2)


def export_tasks_to_ics(tasks, filename="tasks.ics"):
    """
    Takes a list of task dictionaries and exports them as an .ics calendar file.
    Each task should have: person, task, deadline, and status.
    """

    calendar = Calendar()

    for t in tasks:
        event = Event()
        event.name = f"{t.get('person', 'Someone')} - {t.get('task', 'Unnamed Task')}"
        event.description = f"Status: {t.get('status', 'Pending')}"

        deadline_text = t.get("deadline", "")
        event.begin = parse_deadline(deadline_text)
        event.end = event.begin + timedelta(hours=1)

        calendar.events.add(event)

    with open(filename, "w") as f:
        f.writelines(calendar)

    return filename
