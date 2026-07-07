from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

import requests
import os
import time
import base64


# Environment Variables
API_KEY = os.getenv("API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

print("API Key Exists:", bool(API_KEY))
print("GitHub Token Exists:", bool(GITHUB_TOKEN))


app = FastAPI()


# Serve Frontend
@app.get("/")
def serve_ui():
    return FileResponse("index.html")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Input Model
class LogInput(BaseModel):
    log: str
    source: str



# ==========================
# AI FIX AGENT
# ==========================

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
                "content":
                "You are a DevOps expert. Analyze the error and provide a practical short fix."
            },

            {
                "role": "user",
                "content": log
            }

        ]
    }


    try:

        response = requests.post(
            url,
            headers=headers,
            json=data
        )


        result = response.json()

        print("OpenRouter Response:", result)


        if "choices" in result:

            return result["choices"][0]["message"]["content"]


        return "No fix generated"


    except Exception as e:

        print("Fix Agent Error:", e)

        return "Unable to generate fix"



# ==========================
# CREATE GITHUB ISSUE
# ==========================

def create_github_issue(log, fix):

    REPO = "srin8n8-cloud/devops-guardian"


    headers = {

        "Authorization": f"token {GITHUB_TOKEN}",

        "Accept": "application/vnd.github+json"

    }


    data = {

        "title": "Automated DevOps Fix",

        "body":
        f"""
Error:

{log}


Suggested Fix:

{fix}
"""

    }


    try:

        response = requests.post(

            f"https://api.github.com/repos/{REPO}/issues",

            headers=headers,

            json=data

        )


        print("Issue Status:", response.status_code)

        print("Issue Response:", response.json())


        return response.json()



    except Exception as e:

        print("Issue Error:", e)

        return {}





# ==========================
# CREATE GITHUB PR
# ==========================

def create_github_pr(log, fix):

    REPO = "srin8n8-cloud/devops-guardian"


    headers = {

        "Authorization": f"token {GITHUB_TOKEN}",

        "Accept": "application/vnd.github+json"

    }


    try:


        # Get repository details

        repo_response = requests.get(

            f"https://api.github.com/repos/{REPO}",

            headers=headers

        )


        repo_data = repo_response.json()


        base_branch = repo_data["default_branch"]



        # Get latest commit

        ref_response = requests.get(

            f"https://api.github.com/repos/{REPO}/git/ref/heads/{base_branch}",

            headers=headers

        )


        sha = ref_response.json()["object"]["sha"]



        # Create new branch

        branch_name = f"auto-fix-{int(time.time())}"


        branch_response = requests.post(

            f"https://api.github.com/repos/{REPO}/git/refs",

            headers=headers,

            json={

                "ref": f"refs/heads/{branch_name}",

                "sha": sha

            }

        )


        print("Branch Status:", branch_response.status_code)



        # Unique filename

        filename = f"fix-{int(time.time())}.txt"


        content = base64.b64encode(

            f"""
Error:

{log}


Fix:

{fix}
""".encode()

        ).decode()



        # Create file commit

        file_response = requests.put(

            f"https://api.github.com/repos/{REPO}/contents/{filename}",

            headers=headers,

            json={

                "message": "Auto fix commit",

                "content": content,

                "branch": branch_name

            }

        )


        print("File Status:", file_response.status_code)



        # Create PR

        pr_response = requests.post(

            f"https://api.github.com/repos/{REPO}/pulls",

            headers=headers,

            json={

                "title": "Auto Fix by DevOps Guardian",

                "head": branch_name,

                "base": base_branch,

                "body": fix

            }

        )


        print("PR Status:", pr_response.status_code)

        print("PR Response:", pr_response.json())



        return pr_response.json().get(
            "html_url",
            "PR not created"
        )


    except Exception as e:

        print("PR Error:", e)

        return "PR not created"




# ==========================
# VALIDATION AGENT
# ==========================

def validation_agent(log, fix):

    if fix and len(fix) > 20:

        return True


    return False





# ==========================
# MANAGER AGENT
# ==========================

def manager_agent(log):

    max_retries = 2

    attempt = 0



    while attempt < max_retries:


        fix = fix_agent(log)


        if validation_agent(log, fix):


            issue = create_github_issue(
                log,
                fix
            )


            pr_url = create_github_pr(
                log,
                fix
            )



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

                "github_issue":
                issue.get(
                    "html_url",
                    "Issue not created"
                ),

                "github_pr": pr_url,

                "attempts": attempt + 1

            }


        attempt += 1



    return {

        "status": "failed",

        "message": "Could not find valid fix"

    }




# ==========================
# TEST GITHUB TOKEN
# ==========================

@app.get("/github-test")
def github_test():

    headers = {

        "Authorization": f"token {GITHUB_TOKEN}"

    }


    response = requests.get(

        "https://api.github.com/user",

        headers=headers

    )


    return response.json()




# ==========================
# ANALYZE API
# ==========================

@app.post("/analyze")
def analyze_log(data: LogInput):

    return manager_agent(data.log)
