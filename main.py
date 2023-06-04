from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from pathlib import Path
import random
from dotenv import load_dotenv

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_tasks(calendarId: str, start_date: datetime, end_date:datetime):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        events_result = service.events().list(calendarId=calendarId, timeMin=start_date.isoformat()+'T00:00:00Z', timeMax=end_date.isoformat()+'T23:59:59Z', singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if events is not None:
            result = dict()
            for id_event, event in enumerate(events):
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                date_format = '%Y-%m-%dT%H:%M:%S%z'
                if end is not None:
                    end_formated = datetime.strptime(end, date_format)
                if start is not None:
                    start_formated = datetime.strptime(start, date_format)
                result[id_event] = {'start': start_formated, 'task': event['summary'], 'end': end_formated}
            return result
    
    except HttpError as error:
        print('An error occurred: %s' % error)


def get_dates_of_the_current_week() -> set:
    num_week = datetime.today().isocalendar()[1]
    year = datetime.now().year
    first_day = datetime.fromisocalendar(year, num_week, 1).date()
    end_day = first_day + timedelta(days=6)
    return num_week, year, first_day, end_day

def proper_formatting_of_tasks(tasks: dict) -> dict[str: list]:
    if tasks is not None:
        result = dict()
        for task in tasks.values():
            datetime_task = task['start'].strftime('%d.%m.%y')
            start_task = task['start'].strftime('%H:%M')
            end_task = task['end'].strftime('%H:%M')
            if  result.get(datetime_task) is None:
                result[datetime_task] = [f"{start_task} - {end_task}: {task['task']}"]
            else:
                result[datetime_task].append(f"{start_task} - {end_task}: {task['task']}")
        return result

def tasks_dict_to_str(tasks:dict) -> str:
    result = str()
    for date, list_tasks in tasks.items():
        result += f'### {date}\n'
        for task in list_tasks:
            result += f'   - [ ] {task}\n'
    return result


def get_converting_file_to_dict(filecontent:list) -> dict:
    result = dict()
    for line in filecontent:
        if line.startswith('### '):
            start_symbol = line.find(';">')
            line = line.replace('</mark>', '')
            date = line[start_symbol+3:].strip()
        elif any([line.startswith('   - [ ] '),line.startswith('   - [x] ')]):
            line = line.replace('\n', '')
            if result.get(date) is None:
                result[date] = {line[9:]:line+'\n'}
            else:
                result[date] = result[date] | {line[9:]:line+'\n'}
    return result


def update_and_write_tasks(path_file:str, main_tasks:dict):
    with open(path_file, 'r+') as file:
        filecontent = file.readlines()
    
    result = str()
    file_tasks = get_converting_file_to_dict(filecontent)
    for date, tasks in main_tasks.items():
        backgrounds = ['#FF69B4', '#FFD700', '#00FFFF', '#FF8C00', '#00FF00', '#FF0000', '#FFFF00', '#800080', '#0000FF']
        result += f'### <mark style="background: {random.choice(backgrounds)}A6;">{date}</mark>\n'
        if file_tasks.get(date) is None:
            for task in tasks:
                result += f'   - [ ] {task}\n'
        else:
            for task in tasks:
                if file_tasks[date].get(task) is not None:
                    result += file_tasks[date][task]
                else:
                    result += f'   - [ ] {task}\n'
        
    with open(path_file, 'r+') as f:
        content = f.read()
        start_pos = content.find('#tasks\n')
        end_pos = content.find('___\n')
        if start_pos != -1 and end_pos != -1:
            new_content = content[:start_pos] + '#tasks\n' + result + content[end_pos:]
            f.seek(0)
            f.write(new_content)
            f.truncate()




if __name__ == '__main__':
    # print('[INFO] Sync Google-Obsidian start ...')
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    path=os.getenv('path')
    calendarId = os.getenv('calendarId')
    # print('[INFO] Get env values')
    path_file = Path(path)
    num_week, year, first_day, end_day = get_dates_of_the_current_week()
    # print('[INFO] Get Google tasks')
    tasks = get_tasks(calendarId=calendarId, start_date=first_day, end_date=end_day)
    if tasks is not None:
        formated_tasks = proper_formatting_of_tasks(tasks=tasks)
        if formated_tasks is not None:
            path = path_file.joinpath(f'{num_week}.{year}.md')
            if path.exists():
                # print('[INFO] Update tasks in Obsidian ...')
                update_and_write_tasks(path_file=path, main_tasks=formated_tasks)
    # print('[INFO] Sync Google-Obsidian ended')

