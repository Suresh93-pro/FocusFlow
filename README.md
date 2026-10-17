<div align="center">

# ✦ FOCUSFLOW
## Neon Student Productivity Studio

### Focus better. Plan smarter. Make progress visible.

A neon-inspired productivity dashboard made for students — combining tasks, quick notes, focus sessions, study goals and analytics in one desktop app.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-00E5FF?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Storage-SQLite-A238FF?style=for-the-badge&logo=sqlite&logoColor=white)
![No API required](https://img.shields.io/badge/AI%20API-Not%20Required-19E6A3?style=for-the-badge)

</div>

---

## 🌌 Welcome to FocusFlow

**FocusFlow** is a desktop productivity studio for students, built using Python, Tkinter/ttk, Canvas and SQLite. Its dark neon visual style combines animated ambient particles, a vector mascot, bright accent colors, and modular workspace pages.

The aim is straightforward: keep day-to-day study planning in one place, turn focus time into a routine, and make progress easier to review.

## ⚡ What’s inside?

| Module | Highlights |
|---|---|
| **Dashboard** | Neon overview, productivity counters, animated background and vector mascot |
| **My Tasks** | Add, search, filter, complete/reactivate and delete tasks; organize by category, priority and due date |
| **Quick Notes** | Create, edit, search and delete saved notes |
| **Focus Timer** | 15-, 25- and 45-minute focus sessions with start, pause and reset |
| **Study Goals** | A quick view of task completion, focus habit and notes |
| **Analytics** | Task, session, focus-minute and notes summaries with an illustrative weekly activity chart |
| **Calendar** | Calendar information page |
| **Settings** | Settings information page |
| **About Project** | Project modules, technology overview and storage details |

## 🖼️ Visual Showcase

The images below are the project's showcase panels. Open any image to inspect the UI details.

<table>
<tr>
<td width="50%">

**01 · Dashboard**
<br>
<img src="showcase/slide_panel_01.jpg" alt="FocusFlow dashboard design" width="100%">

</td>
<td width="50%">

**02 · Task workspace**
<br>
<img src="showcase/slide_panel_02.jpg" alt="FocusFlow task workspace" width="100%">

</td>
</tr>
<tr>
<td>

**03 · Quick notes**
<br>
<img src="showcase/slide_panel_03.jpg" alt="FocusFlow quick notes interface" width="100%">

</td>
<td>

**04 · Focus timer**
<br>
<img src="showcase/slide_panel_04.jpg" alt="FocusFlow timer interface" width="100%">

</td>
</tr>
<tr>
<td>

**05 · Study goals**
<br>
<img src="showcase/slide_panel_05.jpg" alt="FocusFlow study goals interface" width="100%">

</td>
<td>

**06 · Analytics**
<br>
<img src="showcase/slide_panel_06.jpg" alt="FocusFlow analytics interface" width="100%">

</td>
</tr>
<tr>
<td>

**07 · Calendar**
<br>
<img src="showcase/slide_panel_07.jpg" alt="FocusFlow calendar information page" width="100%">

</td>
<td>

**08 · Settings**
<br>
<img src="showcase/slide_panel_08.jpg" alt="FocusFlow settings information page" width="100%">

</td>
</tr>
<tr>
<td>

**09 · Workspace details**
<br>
<img src="showcase/slide_panel_09.jpg" alt="FocusFlow workspace panel" width="100%">

</td>
<td>

**10 · About FocusFlow**
<br>
<img src="showcase/slide_panel_10.jpg" alt="FocusFlow about project panel" width="100%">

</td>
</tr>
</table>

## 🧰 Technology Stack

- **Python 3** — application logic
- **Tkinter / ttk** — desktop widgets, forms, dialogs and event handling
- **Tkinter Canvas** — custom visuals and animated elements
- **SQLite** — local persistence for tasks, notes and focus sessions

No third-party pip packages, MySQL Workbench, AI assistant or OpenAI API configuration are required.

## 🚀 Run it locally

1. Install Python 3 with Tkinter available.
2. Clone or download this repository.
3. Open the project folder in VS Code or a terminal.
4. Start the app:

   ```bash
   py main.py
   ```

   If the `py` command is not available, try:

   ```bash
   python main.py
   ```

FocusFlow creates `focusflow.db` automatically in the project directory. This database is intentionally not stored in Git; each installation creates its own local records.

## 🗂️ Project structure

```text
FocusFlow/
├── main.py
├── focusflow/
│   ├── __init__.py
│   ├── app.py
│   └── database.py
├── PROJECT_OVERVIEW.txt
├── README.md
├── .gitignore
├── showcase/
│   ├── slide_panel_01.jpg
│   ├── ...
│   └── slide_panel_10.jpg
└── presentation/
    └── FocusFlow_10_Slide_Presentation.pptx
```

## 🎓 Project details

**Project:** FocusFlow — Neon Student Productivity Studio  
**Prepared by:** G Suresh Reddy  
**Program:** B.Tech — CSE (Cybersecurity)  
**Technologies:** Python, Tkinter, ttk, Canvas and SQLite

The `presentation/` directory includes a 10-slide PowerPoint overview of the project and its interface.

## 🔐 Data & privacy

- Tasks, notes and focus sessions are stored locally in `focusflow.db`.
- The database is excluded from version control so personal study content is not published accidentally.
- This project does not require an API key or send task/notes data to an AI service.

## 🛣️ Possible next steps

- A richer calendar with reminders
- Exportable study summaries
- Configurable focus-session presets
- Optional dark/neon theme customization
- Backup and restore for the local database

---

<div align="center">

**FOCUSFLOW** · *Small steps. Big results.* ✦

</div>
