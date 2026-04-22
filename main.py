from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Input format
class LogInput(BaseModel):
    log: str
    source: str


# 🔹 Your OpenRouter API Key (PUT YOUR REAL KEY HERE)
API_KEY = os.getenv("API_KEY")


# 🔹 FIX AGENT (AI-powered)
def fix_agent(log):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a DevOps expert. Give a short fix."
            },
            {
                "role": "user",
                "content": log
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        # Debug (optional)
        print("API Response:", result)

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("Error in fix_agent:", e)
        return "Unable to generate fix. Check API key or API response."


def create_github_issue(log, fix):
    url = "https://api.github.com/repos/srin8n8-cloud/devops-guardian/issues"

    headers = {
        "Authorization": os.getenv("GITHUB_TOKEN1"),
        "Accept": "application/vnd.github+json"
    }

    data = {
        "title": "Automated DevOps Fix",
        "body": f"Error:\n{log}\n\nSuggested Fix:\n{fix}"
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        print("GitHub Status:", response.status_code)
        print("GitHub Response:", response.text)

        return response.json()

    except Exception as e:
        print("GitHub Error:", e)
        return {}
def create_github_pr(log, fix):
    import requests
    import time
    import base64

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")   
    REPO = "srin8n8-cloud/devops-guardian"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        # Step 1: Get default branch
        repo_url = f"https://api.github.com/repos/{REPO}"
        repo_data = requests.get(repo_url, headers=headers).json()
        base_branch = repo_data["default_branch"]

        # Step 2: Get latest commit SHA
        ref_url = f"https://api.github.com/repos/{REPO}/git/ref/heads/{base_branch}"
        ref_data = requests.get(ref_url, headers=headers).json()
        sha = ref_data["object"]["sha"]

        # Step 3: Create new branch
        branch_name = f"auto-fix-{int(time.time())}"

        branch_res = requests.post(
            f"https://api.github.com/repos/{REPO}/git/refs",
            headers=headers,
            json={
                "ref": f"refs/heads/{branch_name}",
                "sha": sha
            }
        )
        print("Branch Status:", branch_res.status_code)

        # Step 4: Create file
        content = base64.b64encode(
            f"Error:\n{log}\n\nFix:\n{fix}".encode()
        ).decode()

        file_res = requests.put(
            f"https://api.github.com/repos/{REPO}/contents/fix.txt",
            headers=headers,
            json={
                "message": "Auto fix commit",
                "content": content,
                "branch": branch_name
            }
        )
        print("File Status:", file_res.status_code)

        # Step 5: Create Pull Request
        pr = requests.post(
            f"https://api.github.com/repos/{REPO}/pulls",
            headers=headers,
            json={
                "title": "Auto Fix by DevOps Guardian",
                "head": branch_name,
                "base": base_branch,
                "body": f"Automated fix:\n\n{fix}"
            }
        )

        # ✅ DEBUG (inside function)
        print("PR Status:", pr.status_code)
        print("PR Response:", pr.json())

        return pr.json().get("html_url", "PR not created")

    except Exception as e:
        print("PR Error:", e)
        return "PR not created"
    # 🔹 VALIDATION AGENT
def validation_agent(log, fix):
    fix = fix.lower()

    if "install" in fix:
        return True
    if "check" in fix:
        return True
    if "verify" in fix:
        return True

    return False


# 🔹 MANAGER AGENT (controls flow + retry)
def manager_agent(log):
    max_retries = 2
    attempt = 0

    while attempt < max_retries:
        fix = fix_agent(log)
        valid = validation_agent(log, fix)

        if valid:
            #  CALL BOTH FUNCTIONS
            issue = create_github_issue(log, fix)
            pr_url = create_github_pr(log, fix)

            #  Detect error type
            if "ModuleNotFoundError" in log:
                error_type = "Python Dependency Error"
            elif "SyntaxError" in log:
                error_type = "Syntax Issue"
            elif "docker" in log.lower():
                error_type = "Docker Issue"
            else:
                error_type = "General DevOps Error"

            return {
                "status": "success",
                "error_type": error_type,
                "fix": fix,
                "github_issue": issue.get("html_url", "Issue not created"),
                "github_pr": pr_url,
                "attempts": attempt + 1
            }

        attempt += 1

    return {
        "status": "failed",
        "message": "Could not find valid fix"
    }
# 🔹 API Endpoint
@app.post("/analyze")
def analyze_log(data: LogInput):
    return manager_agent(data.log)