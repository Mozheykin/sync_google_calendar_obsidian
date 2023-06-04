# About
Synchronization of events between google calendar and obsidian local storage.
This script transfers events to weekly notes.
# Samples
![](https://i.imgur.com/mdQPLWV.png)
![](https://i.imgur.com/DJYIYFZ.png)
![](https://i.imgur.com/iEnYdAa.png)
# Install
* git clone https://github.com/Mozheykin/sync_google_calendar_obsidian.git
* pip install -r requrements.txt
* create google API https://support.google.com/googleapi/answer/6158862?hl=en
* download client_secret.json and move in project folder
* copy calendar id
* create file `.env` \
    calendarId=9qhhv7ho@group.calendar.google.com \
    path=/home/legal/github/Obsidian/re/1.Projects(Проекты)/
* add in obsidian `#test` and end module `___`
* start script `python3 main.py`