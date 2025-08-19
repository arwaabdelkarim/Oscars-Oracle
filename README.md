# 🎬 Oscars-Oracle

Oscars-Oracle is a Python desktop application that allows users to explore, analyze, and nominate Oscar candidates. The app features user authentication, nomination tracking, and a rich set of data-driven insights — all through a friendly GUI built with Tkinter.

---

## 📦 Quick Start (Windows Executable)

✅ If you're on **Windows**, you can run the app instantly:

> **Download and run:** [`gui.exe`](./gui.exe)

No Python installation or setup required!

---

## 📸 Demo

🎥 [Click to watch the app in action](https://m.youtube.com/watch?v=N3D52gPo6Pg)

---

## 💡 Features

- 🔐 **User Authentication**
  - Sign up and log in to personalize your experience.

- 🏆 **Nominations**
  - ➕ Add a new nomination: nominate a previously nominated person for a role.
  - 👁 View *your* nominations.
  - 📊 View top nominated movies by system users (filterable by category or iteration).

- 🔎 **Insights and Analytics**
  - 🧑‍🎤 See total nominations and Oscar wins for a specific actor or actress.
  - 🌍 View top 5 birth countries for Best Leading Actor award winners.
  - 🌐 Find all nominated staff members born in a specific country.
  - 💭 Living Dream Team: actors who won Oscars and are still alive.
  - 🏢 Top 5 production companies based on the number of Oscars won.
  - 🗣 List all non-English speaking movies that won Oscars, along with the year.

---

## 🛠 Technologies Used

- 🐍 Python 3
- 🖼 Tkinter (GUI)
- 🗃 MySQL (Database) using MySQL Workbench
- 🌐 BeautifulSoup / requests (Web scraping)
- 🧰 PyInstaller (for creating the `.exe`)

---

## 📂 Project Structure

```
Oscars-Oracle/
├── db.py         # Database functions and setup
├── gui.py        # Main application with Tkinter GUI
├── gui.exe       # Windows executable version
├── demo.mp4      # App walkthrough demo
├── README.md     # This file
├── LICENSE
```

---

## 📌 Notes

- Each user's nominations are saved separately.
- All data is stored and queried from a MySQL database designed using MySQL Workbench.
- Input is validated to avoid duplicate or invalid nominations.
- `.exe` was generated using PyInstaller:
  
```bash
pyinstaller --onefile gui.py
```

---

## 📄 License

Licensed under the [Apache-2.0 License](LICENSE).

---

## 👩‍💻 Author

Built with ❤️ by **Arwa Abdelkarim**  
GitHub: [@arwaabdelkarim](https://github.com/arwaabdelkarim)
