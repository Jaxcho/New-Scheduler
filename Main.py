import PySimpleGUI as gui
import datetime
import os
import time
import pytz
import threading
import json

SYMBOL_UP = '▲'
SYMBOL_DOWN = '▼'
opened1 = True

tz = pytz.timezone("US/Pacific")

day = datetime.datetime.now(tz=tz)
current_time = day
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

day1 = day.weekday()
gui.theme('Light Green')

width = 800
height = 600

time1 = 0


def addtime(time, min):
    if min == None:
        min = 0
    time = datetime.datetime.strptime(time, "%x %X")

    dt = datetime.datetime(time.year, time.month, time.day, time.hour, time.minute)
    dt = dt + datetime.timedelta(minutes=min)
    return dt


def generate_schedule(schedules):
    schedule = []
    for task, time in schedules.items():
        schedule.append([task, time])

    return [gui.pin(gui.Table(schedule, headings=["task", "time"], expand_x=True, col_widths=[50, 100], key=sched[-1]),
                    expand_x=True)]


def schedule(tasks, title, time):
    global currentsched
    schedules = {}
    a = 0
    for key, val in tasks.items():

        if val is None:
            continue
        a += val
        schedules[key] = addtime(time, a)
    currentsched = schedules
    return schedules


def combine(tasks, vals, times):
    for key, val in vals.items():
        if key == "Title" or val == None:
            continue
        try:
            tasks[val] = times[key]
        except KeyError:
            continue
    return tasks


def create_thread(window):
    while True:
        time.sleep(0.1)
        window.write_event_value('update', None)
        window.write_event_value('change_task', None)


main_layout = [
    [gui.Text(days[day1]), gui.Text(day, key="clock")],
    [gui.Button('Add row', key='Add'), ],

    [gui.Text("Title: "), gui.Input(key='Title', enable_events=True)],
    [gui.Col([], key='Col', scrollable=True, vertical_scroll_only=True, size=(width, height // 4))],
    [gui.Button('Schedule', key='Schedule')],
    [gui.Col([], key='Schedules', scrollable=True, vertical_scroll_only=True, size=(width, height // 2))],
    [gui.Text(key='Task')]
]

home_layout = [
    [
        gui.Button("Start", key="Start", enable_events=True),

    ]
]
def collapse(layout, key):
    return gui.pin(gui.Col(layout, key=key))


layout = [
    [gui.Column(home_layout, key='home')],
    [gui.Column(main_layout, key='main', visible=False, size=(width, height), scrollable=True,
                vertical_scroll_only=True)]

]

layout1 = []


def generate_row(key1):
    time = 0
    return [gui.pin(
        gui.Col([[
            gui.Button('X', border_width=0, button_color=(gui.theme_text_color(), gui.theme_background_color()),
                       key=('Delete', key1)),
            gui.Input(key=key1),
            gui.Text(time1, key=f'time {key1}'),
            gui.Button('Down 5', key=(f'Down 5 {key1}', key1)),
            gui.Button('Up 5', key=(f'Up 5 {key1}', key1)),

        ],
            [gui.T(SYMBOL_DOWN, enable_events=True, key=(f'open section {key1}', key1), text_color='black'),
             gui.T(f'Section {key1}', enable_events=True, key=(f'open section', key1))],
            [collapse([
                [gui.Input(key=f'notes {key1}')]
            ], f"section {key1}")],
        ], key=("Row", key1))
    )]


times = {}

currentsched = {}

tasks = {}

notes = {}


def current_task():
    # print(currentsched)
    task_names = list(currentsched.keys())
    # task_names=task_names
    for i, val in enumerate(task_names):
        t = int(currentsched[val].strftime('%H'))
        m = int(currentsched[val].strftime('%M'))
        dt = datetime.datetime.strptime(current_time, "%x %X")

        if int(dt.strftime('%H')) * 60 + int(dt.strftime('%M')) <= 60 * t + m:
            task = val
            return task
    return "Done"


def savetimes(times, notes, tasks, title='', file_name="times.json"):
    print("times:", times, "\nnotes:",notes,"\ntasks:", tasks,"\ntitle:", title)
    saved={}
    for i, (key, val) in enumerate(tasks.items()):
        try:
            # if i == 0:
            #     continue
            if times[str(i)]==None or val == None or len(key) == 0:
                continue
            saved.update({key:[val, notes[str(i)]]})
            print({key:[val, notes[str(i)]]})
        except KeyError:
            continue
    print(saved)
    with open('Saved.json', 'w') as f:
        json.dump(saved, f, indent=2)

    # if len(tasks) == 0:
    #     tasks = {}
    # nonnone = {}
    # for i, val in enumerate(times):
    #     if times[val] == None:
    #         continue
    #     try:
    #         nonnone[tasks[val]] = (times[val])
    #     except KeyError:
    #         nonnone[i] = times[val]
    #     except TypeError:
    #         continue
    # with open(file_name, 'w') as file:
    #     json.dump(times, file, indent=2)
    # with open("tasks.json", "w") as file2:
    #     json.dump(tasks, file2, indent=2)
    # with open("title.json", 'w') as file:
    #     json.dump({"title": title}, file, indent=2)
    # with open("notes.json", 'w') as file:
    #     json.dump(notes, file, indent=2)
    # # with
    # return nonnone

def savetitle(title):
    with open('title.json', 'w') as f:
        json.dump(title, f, indent=2)

def loadtitle(window):
    title=''
    try:
        with open('title.json', 'r') as file:
            title = json.load(file)
    except FileNotFoundError:
        title=''
    window['Title'].update(value=title)
    return window



def loadtimes(window, file_name="Saved.json"):

    values = {}
    try:
        with open("Saved.json", 'r') as file:
            values = json.load(file)
    except FileNotFoundError:
        values = {}
    print(values, 'val')

    """
    task_name: [duration, note]
    
    """
    title = {}
    # notess = {}

    for task, note_duration in values.items():
        time, note = note_duration
        if time is None or time == None:
            continue
        val = str(window.metadata)

        times.update({str(window.metadata): time})
        window.extend_layout(window['Col'], [generate_row(f'{window.metadata}')])
        window[f"{window.metadata}"].update(value=task)
        window[f"time {window.metadata}"].update(value=time)
        #
        # window['Title'].update(value=title['title'])
        window.refresh()
        window['Col'].contents_changed()
    #
    # for val, note in notess.items():
    #     if f'notes {task}' not in vals:
    #       continue
    #
        notes.update({val: note})
    #
        window[f"notes {val}"].update(value=note)
        window.refresh()
        window["Col"].contents_changed()
        window.metadata += 1



def change_time(tasks, vals, times):
    window[f'time {evt[1]}'].update(value=times[evt[1]])
    updatetime(times)

    tasks = combine(tasks, vals, times)
    title = vals['Title']
    savetimes(times, notes, tasks, title)


def updatetime(times):
    for time, val in times.items():
        if val == None:
            continue
        times.update({time: val})


window = gui.Window("Hello", layout, size=(800, 600), metadata=0)

window.read()

threading.Thread(target=create_thread, args=(window,), daemon=True).start()

title = ''
sched = []

while True:

    evt, vals = window.read()
    if evt == gui.WIN_CLOSED or evt == "Exit":
        break

    for val, eval in vals.items():
        if val in times and times[val] != None and len(vals[val]) > 0:
            tasks.update({vals[val]: times[val]})
        if str(val).isdigit() and f"notes {val}" in vals:
            note = vals[f'notes {val}']
            """
            """
            if times[val]!=None:

                notes.update({val: note})
            print({val:note}, 'NOTE')

    # for val in vals:

    remove = []
    for key, val in tasks.items():
        if key not in vals.values():
            remove.append(key)
    for key in remove:
        del tasks[key]
    if evt == 'Title':
        title = vals['Title']

        savetimes(times, notes, tasks, title)
        savetitle(title)
    if evt == 'change_task':
        window['Task'].update(value=current_task())
        savetimes(times, notes, tasks, title)
    if evt == 'Schedule':
        if len(sched) >= 1:
            window[sched[-1]].update(visible=False)
        sched.append(len(sched))
        tasks = combine(tasks, vals, times)
        title = vals['Title']
        savetimes(times, notes, tasks, title)
        schedules = schedule(tasks, '', datetime.datetime.now(tz=tz).strftime('%x %X'))
        window.extend_layout(window['Schedules'], [generate_schedule(schedules)])
        window.refresh()
        window['Schedules'].contents_changed()
    if evt == "Start":
        window['home'].update(visible=False)
        window['main'].update(visible=True)
        loadtimes(window)
        print("load")
        loadtitle(window)

    if 'open section' in evt[0]:
        opened1 = not opened1
        window[(f'open section {evt[1]}', evt[1])].update(SYMBOL_DOWN if opened1 else SYMBOL_UP)
        window[f'section {evt[1]}'].update(visible=opened1)

    if 'Down 5' in evt[0]:
        if times[evt[1]] <= 0:
            continue
        times[evt[1]] -= 5

        change_time(tasks, vals, times)
    if evt == 'Add':
        times.update({str(window.metadata): 0})
        savetimes(times, notes, tasks, title)
        window.extend_layout(window['Col'], [generate_row(f'{window.metadata}')])
        window.refresh()
        window['Col'].contents_changed()

        updatetime(times)
        tasks = combine(tasks, vals, times)
        title = vals['Title']
        savetimes(times, notes, tasks, title)
        window.metadata += 1


    if evt[0] == 'Delete':
        window[('Row', evt[1])].update(visible=False)
        times[evt[1]] = None
        tasks[evt[1]] = None
        updatetime(times)
        tasks = combine(tasks, vals, times)
        title = vals['Title']
        savetimes(times, notes, tasks, title)
    if 'Up 5' in evt[0]:
        times[evt[1]] += 5
        change_time(tasks, vals, times)
    if evt == "update":
        current_time = datetime.datetime.now(tz=tz).strftime("%x %X")
        window['clock'].update(value=current_time)

window.close()
savetitle(title)
savetimes(times, notes, tasks, title)
# loadtimes(window)