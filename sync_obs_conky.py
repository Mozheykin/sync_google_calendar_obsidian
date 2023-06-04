from datetime import datetime, timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

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

def get_dates_of_the_current_week() -> set:
    num_week = datetime.today().isocalendar()[1]
    year = datetime.now().year
    first_day = datetime.fromisocalendar(year, num_week, 1).date()
    end_day = first_day + timedelta(days=6)
    return num_week, year, first_day, end_day

def print_conky(list_tasks:list) -> None:
    for task in list_tasks:
        print(task)

def replace_task_status(task:str) -> str:
    if '   - [ ] ' in task:
        task = task.replace('   - [ ]', '[X]')
    elif '   - [x] ' in task:
        task = task.replace('   - [x]', '[V]')
    task = task.replace('\n', '')
    return task

def main():
    num_week, year, *_ = get_dates_of_the_current_week()
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    path=os.getenv('path')
    path_file = Path(path)
    path = path_file.joinpath(f'{num_week}.{year}.md')
    if path.exists():
        with open(path, 'r') as file:
            filecontent = file.readlines()
        file_tasks = get_converting_file_to_dict(filecontent)
        # pprint(file_tasks)
        today = datetime.today().strftime('%d.%m.%y')
        tasks_today = file_tasks.get(today)
        if tasks_today is not None:
            conky_tasks = [replace_task_status(task) for task in tasks_today.values()]
            print_conky(conky_tasks)
    

if __name__ == '__main__':
    main()