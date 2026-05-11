import os
import re
import requests
import sys

GROUP_LIMITS = {
    "admin": 14,
    "Professors": 14,
    "Graduates": 7,
    "Students": 1
}

ORG_NAME = "KAU-H200"

def get_user_group_from_teams(username, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    teams_to_check = ["admin", "professors", "graduates", "students"]
    for team_slug in teams_to_check:
        url = f"https://api.github.com/orgs/{ORG_NAME}/teams/{team_slug}/memberships/{username}"
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                mapping = {"admin": "admin", "professors": "Professors", "graduates": "Graduates", "students": "Students"}
                return mapping[team_slug]
        except Exception:
            continue
    return None

def post_comment(issue_num, token, repo, body):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_num}/comments"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    res = requests.post(url, json={"body": body}, headers=headers)
    print(f"post_comment status: {res.status_code}", flush=True)

def fail_process(issue_num, token, repo, msg):
    post_comment(issue_num, token, repo, msg)
    print(msg)
    sys.exit(1)

def process():
    issue_body        = os.getenv("ISSUE_BODY", "")
    actual_sender     = os.getenv("ACTUAL_SENDER", "")
    jenkins_url       = os.getenv("JENKINS_URL")
    jenkins_token     = os.getenv("JENKINS_TOKEN")
    issue_number      = os.getenv("ISSUE_NUMBER")
    github_token      = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")
    print(f"ISSUE_NUMBER: {issue_number}", flush=True)
    print(f"GITHUB_REPOSITORY: {github_repository}", flush=True)
    print(f"GITHUB_TOKEN 존재: {bool(github_token)}", flush=True)
    print(f"ACTUAL_SENDER: {actual_sender}", flush=True)
    def extract_val(label_pattern):
        match = re.search(fr'### {label_pattern}\s*\n+\s*(.*)', issue_body)
        return match.group(1).strip() if match else None

    requested_user = extract_val(r"사용자 ID \(Username\)")
    git_repo       = extract_val(r"실행할 코드의 GitHub 링크")
    exec_command   = extract_val(r"코드 실행 명령어")
    image_type     = extract_val(r"사용할 이미지 선택")
    language       = extract_val(r"사용 언어 \(Language\)")
    mig_count      = extract_val(r"GPU 할당량 \(MIG 갯수\)")

    # 1. 사용자 ID 검증
    if requested_user != actual_sender:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ 검증 실패: 입력된 ID(`{requested_user}`)와 실제 작성자(`{actual_sender}`)가 다릅니다.")

    post_comment(issue_number, github_token, github_repository,
                 f"✅ **사용자 확인 완료:** `{actual_sender}` 본인 확인이 되었습니다.")

    # 2. 팀 멤버 검증
    user_group = get_user_group_from_teams(actual_sender, github_token)

    if not user_group:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ 권한 없음: `{actual_sender}`님은 {ORG_NAME} 조직의 등록된 팀 멤버가 아닙니다.")

    post_comment(issue_number, github_token, github_repository,
                 f"✅ **권한 확인 완료:** `{actual_sender}`님은 `{user_group}` 그룹 멤버입니다.")

    # 3. GPU 할당량 검증
    limit = GROUP_LIMITS.get(user_group, 0)
    mig_count_int = int(mig_count) if mig_count and mig_count.isdigit() else 0

    if mig_count_int > limit:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ 할당량 초과: `{user_group}` 그룹의 최대 할당량은 {limit}개입니다.")

    post_comment(issue_number, github_token, github_repository,
                 f"✅ **GPU 할당량 확인 완료:** 요청 {mig_count_int}개 / 그룹 한도 {limit}개 → 통과!")

    payload = {
        "user":              requested_user,
        "group":             user_group,
        "git_repo":          git_repo,
        "exec_command":      exec_command,
        "image":             image_type,
        "language":          language,
        "mig_count":         mig_count_int,
        "issue_number":      issue_number,
        "github_repository": github_repository.split('/')[-1]
    }

    webhook_url = f"{jenkins_url}/generic-webhook-trigger/invoke?token={jenkins_token}"

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        if res.status_code == 200:
            success_msg = (
                f"### ✅ 접수 완료! (그룹: `{user_group}`)\n\n"
                f"- 요청 자원: MIG {mig_count_int}개 (그룹 한도: {limit}개)\n"
                f"- 이미지: `{image_type}`\n"
                f"- 명령어: `{exec_command}`\n\n"
                f"Kueue 대기열(FIFO)에 등록되었습니다. 자원이 할당되는 대로 학습이 시작됩니다!"
            )
            post_comment(issue_number, github_token, github_repository, success_msg)
        else:
            print(f"Jenkins error: {res.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process()
