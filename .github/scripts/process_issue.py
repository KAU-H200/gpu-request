import os
import re
import json
import requests
import sys

GROUP_LIMITS = {
    "admin": 7,
    "Professors": 7,
    "Graduates": 7,
    "Students": 1
}

ORG_NAME = "Aerodrone-H200"
MAPPING_FILE = "user-mapping.json"
# ★ 매핑 파일은 실행 레포(gpu-request)가 아니라 gpu-infrastructure 레포에 있다.
#   레포 이름만 변수로 빼두어 org/파일 위치가 바뀌어도 한 줄만 고치면 되게 함.
MAPPING_REPO = "gpu-infrastructure"
MAPPING_BRANCH = "main"


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


def load_user_mapping(token):
    """매핑 파일이 다른 레포(gpu-infrastructure)에 있으므로 GitHub Contents API로 읽어온다.

    - Accept 헤더를 v3.raw 로 주면 base64 디코딩 없이 파일 내용을 그대로 받는다.
    - private 레포이므로 token 에 해당 레포 읽기 권한(Contents: read)이 있어야 한다.
    """
    url = f"https://api.github.com/repos/{ORG_NAME}/{MAPPING_REPO}/contents/{MAPPING_FILE}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.raw",
    }
    params = {"ref": MAPPING_BRANCH}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return json.loads(res.text)
        else:
            print(f"매핑 파일 로드 실패: HTTP {res.status_code} - {res.text[:200]}", flush=True)
            return {}
    except Exception as e:
        print(f"매핑 파일 로드 오류: {e}", flush=True)
        return {}


def post_comment(issue_num, token, repo, body):
    if not (issue_num and token and repo):
        print(f"⚠️ 댓글 작성 불가 - 필수값 누락 (issue={issue_num}, repo={repo}, token={bool(token)})", flush=True)
        return
    try:
        url = f"https://api.github.com/repos/{repo}/issues/{issue_num}/comments"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        res = requests.post(url, json={"body": body}, headers=headers, timeout=10)
        print(f"post_comment status: {res.status_code}", flush=True)
        if res.status_code >= 300:
            print(f"⚠️ 댓글 API 응답: {res.text[:300]}", flush=True)
    except Exception as e:
        print(f"⚠️ 댓글 작성 중 예외: {e}", flush=True)


def fail_process(issue_num, token, repo, msg):
    post_comment(issue_num, token, repo, msg)
    print(msg, flush=True)
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

    if not issue_number or not github_token or not github_repository:
        print("❌ 치명적: issue_number/github_token/github_repository 중 누락. 댓글 작성 불가.", flush=True)
        sys.exit(1)

    def extract_val(label_pattern):
        match = re.search(fr'### {label_pattern}\s*\n+\s*(.*)', issue_body)
        return match.group(1).strip() if match else None

    requested_user = extract_val(r"사용자 ID \(Username\)")
    git_repo       = extract_val(r"실행할 코드의 GitHub 링크")
    exec_command   = extract_val(r"코드 실행 명령어")
    image_type     = extract_val(r"사용할 이미지 선택")
    language       = extract_val(r"사용 언어 \(Language\)")
    mig_count      = extract_val(r"GPU 할당량 \(MIG 갯수\)")

    missing = []
    if not requested_user: missing.append("사용자 ID")
    if not git_repo:       missing.append("GitHub 링크")
    if not exec_command:   missing.append("실행 명령어")
    if not image_type:     missing.append("이미지 선택")
    if not mig_count:      missing.append("GPU 할당량")
    if missing:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **이슈 형식 오류:** 다음 항목을 읽을 수 없습니다 → {', '.join(missing)}\n"
                     f"이슈 템플릿 형식에 맞게 작성했는지 확인해주세요.")

    if requested_user != actual_sender:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **검증 실패:** 입력된 ID(`{requested_user}`)와 실제 작성자(`{actual_sender}`)가 다릅니다.")

    post_comment(issue_number, github_token, github_repository,
                 f"✅ **사용자 확인 완료:** `{actual_sender}` 본인 확인이 되었습니다.")

    user_group = get_user_group_from_teams(actual_sender, github_token)
    if not user_group:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **권한 없음:** `{actual_sender}`님은 {ORG_NAME} 조직의 등록된 팀 멤버가 아닙니다.")

    post_comment(issue_number, github_token, github_repository,
                 f"✅ **권한 확인 완료:** `{actual_sender}`님은 `{user_group}` 그룹 멤버입니다.")

    limit = GROUP_LIMITS.get(user_group, 0)
    mig_count_int = int(mig_count) if mig_count and mig_count.isdigit() else 0
    if mig_count_int not in (1, 7):
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **잘못된 할당량:** `{mig_count}` 는 허용되지 않습니다. (1 또는 7만 가능)")
    if mig_count_int > limit:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **할당량 초과:** `{user_group}` 그룹의 최대 할당량은 {limit}입니다. (요청: {mig_count_int})")

    post_comment(issue_number, github_token, github_repository,
                 f"✅ **GPU 할당량 확인 완료:** 요청 {mig_count_int} / 그룹 한도 {limit} → 통과!")

    user_mapping = load_user_mapping(github_token)
    user_info = user_mapping.get(actual_sender)

    if not user_info:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **신원 매핑 없음:** `{actual_sender}`님의 이름·학번 정보가 등록되어 있지 않습니다.\n"
                     f"관리자에게 `{MAPPING_REPO}` 레포의 `{MAPPING_FILE}` 에 본인 정보 등록을 요청하세요.")

    applicant_name  = user_info.get("name", "")
    applicant_haksa = user_info.get("haksa", "")

    if not applicant_name or not applicant_haksa:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **신원 매핑 불완전:** `{actual_sender}`님의 이름 또는 학번 정보가 누락되었습니다.")

    post_comment(issue_number, github_token, github_repository,
                 "✅ **신원 매칭 완료**")

    payload = {
        "user":              requested_user,
        "group":             user_group,
        "git_repo":          git_repo,
        "exec_command":      exec_command,
        "image":             image_type,
        "language":          language,
        "mig_count":         mig_count_int,
        "issue_number":      issue_number,
        "github_repository": github_repository.split('/')[-1],
        "applicant_name":    applicant_name,
        "applicant_haksa":   applicant_haksa
    }

    if not jenkins_url or not jenkins_token:
        fail_process(issue_number, github_token, github_repository,
                     "❌ **시스템 오류:** Jenkins 연결 정보가 설정되지 않았습니다. 관리자에게 문의하세요.")

    webhook_url = f"{jenkins_url}/generic-webhook-trigger/invoke?token={jenkins_token}"

    try:
        res = requests.post(webhook_url, json=payload, timeout=10)
        if res.status_code == 200:
            kind = "GPU 1장 통째" if mig_count_int == 7 else "MIG 슬라이스"
            success_msg = (
                f"### ✅ 1차 검증 완료! (그룹: `{user_group}`)\n\n"
                f"- 신청자: {applicant_name} ({applicant_haksa})\n"
                f"- 요청 자원: {mig_count_int} ({kind})\n"
                f"- 이미지: `{image_type}`\n"
                f"- 명령어: `{exec_command}`\n\n"
                f"Jenkins로 전달되었습니다. **예약 시간 검증 후** 자원이 할당됩니다."
            )
            post_comment(issue_number, github_token, github_repository, success_msg)
        else:
            fail_process(issue_number, github_token, github_repository,
                         f"❌ **Jenkins 전송 실패:** 응답 코드 {res.status_code}. 관리자에게 문의하세요.")
    except Exception as e:
        fail_process(issue_number, github_token, github_repository,
                     f"❌ **Jenkins 연결 오류:** {str(e)[:200]}\n관리자에게 문의하세요.")


if __name__ == "__main__":
    try:
        process()
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        issue_number      = os.getenv("ISSUE_NUMBER")
        github_token      = os.getenv("GITHUB_TOKEN")
        github_repository = os.getenv("GITHUB_REPOSITORY")
        post_comment(issue_number, github_token, github_repository,
                     f"⚠️ **검증 처리 중 오류 발생**\n\n```\n{str(e)[:500]}\n```\n관리자에게 문의하세요.")
        sys.exit(1)
