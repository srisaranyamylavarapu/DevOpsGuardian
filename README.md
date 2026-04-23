# 🚀 DevOps Guardian

AI-powered DevOps agent that analyzes error logs, suggests fixes, and automatically creates GitHub Issues and Pull Requests.

---

## 🌐 Live Demo

https://devopsguardian.onrender.com

---

## 🧠 Overview

DevOps Guardian is an intelligent agent that:

* 📥 Takes error logs as input
* 🤖 Uses AI to generate a fix
* ✅ Validates the fix
* 🐞 Automatically creates a GitHub Issue
* 🚀 Automatically creates a GitHub Pull Request

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **Frontend:** HTML, CSS, JavaScript
* **AI Model:** OpenRouter (LLM)
* **Automation:** GitHub API
* **Deployment:** Render

---

## 🧩 How It Works

```plaintext
User Input → FastAPI Backend → AI (OpenRouter)
         → Fix Generated → Validation
         → GitHub Issue + Pull Request Created
```

---

## ▶️ How to Run Locally

```bash
# Clone repository
git clone https://github.com/srisaranyamylavarapu/DevOpsGuardian

# Navigate into folder
cd DevOpsGuardian

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload
```

Open `index.html` in your browser.

---

## 🔐 Environment Variables

Create a `.env` file:

```env
API_KEY=your_openrouter_api_key
GITHUB_TOKEN=your_github_token
```

---

## 🧪 Sample Test Case

```plaintext
ModuleNotFoundError: No module named numpy
```

---

## 📸 Screenshot

(Add your UI image here)

```md
![UI Screenshot](your-image-link)
```

---

## 🎥 Demo Video (Optional)

(Add your video link)

```md
[Watch Demo](your-video-link)
```

---

## 🎯 Use Case

* Automates debugging in DevOps workflows
* Reduces manual error fixing effort
* Helps teams maintain faster deployment cycles

---

## 🚀 Future Improvements

* Better UI/UX
* Support for more error types
* Multi-agent architecture
* CI/CD integration

---

## 👨‍💻 Author

Mylavarapu Sri Saranya 

---
