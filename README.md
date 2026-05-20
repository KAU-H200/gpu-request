# 🖥️ 항공드론 H200 GPU 사용 요청

> **Drone Business Unit · GPU Infrastructure**  
> NVIDIA H200 클러스터에서 코드를 실행하기 위한 공개 요청 레포지토리입니다.

---

## 📌 이 레포지토리의 목적

이 레포지토리는 **코드 실행 요청서(이슈)만 작성하는 공간**입니다.  
FaaS 형태의 서비스로 함수로 요청처리를 하도록 자동화 되어있습니다.
실제 인프라 코드와 GPU 클러스터는 별도의 Private 레포지토리에서 관리되며,  
요청서를 제출하면 이후 모든 과정은 **자동화 파이프라인이 처리**합니다.

```
이슈 제출 (여기) → GitHub Actions 검증 → Jenkins 파이프라인 → H200 실행 → 결과 반환
```

---

## 👥 그룹별 권한 및 MIG 슬라이스 한도

| 그룹 | 역할 | MIG 슬라이스 최대 | 주요 권한 |
|------|------|:-----------------:|-----------|
| **Admins** | 시스템 관리자 | 7개 | 전체 관리 및 설정 |
| **Maintainers** | 운영 담당자 | 7개 | 이슈 승인 및 파이프라인 제어 |
| **Developers** | 개발자 | 3개 | 요청서 작성 및 코드 실행 |
| **Guests** | 외부 협력자 | 1개 | 결과 조회 및 제한적 요청 |

> 그룹은 GitHub Organization의 Teams 기능으로 관리됩니다.  
> **초대는 관리자(Admins)가 수행**합니다. 초대 이메일을 수락한 후 이슈를 작성할 수 있습니다.

---

## 🚀 사용 절차

### Step 1 — Organization 초대 수락
관리자로부터 `항공드론 사업단 H200` Organization 초대 이메일을 수락합니다.

### Step 2 — 이슈 작성
상단 **Issues** 탭 → **New issue** → **컨테이너 생성 및 코드 실행 요청** 템플릿 선택

아래 항목을 모두 정확히 입력합니다.

| 항목 | 설명 | 예시 |
|------|------|------|
| 사용자 ID | 본인의 GitHub Username | `kau-student01` |
| GitHub 링크 | 실행할 코드 레포지토리 주소 | `https://github.com/username/repo.git` |
| 실행 명령어 | 코드 시작 명령어 | `pip install --upgrade torch==2.6.0 torchvision && python main.py` |
| 사용 이미지 | Docker 이미지 선택 | `pytorch/pytorch:latest` |
| 사용 언어 | Python / Bash | `Python` |
| GPU 할당량 | MIG 슬라이스 수 (그룹 한도 내) | `1` |

#### 📦 추가 필요 모듈 작성 방법

기본 이미지(`kau/pytorch-master`, `kau/tensorflow-master`)에 포함되지 않은 패키지가 필요할 경우 작성합니다.  

아래는 이미 설치되어 있으므로 입력 불필요
<table>
  <tr>
    <td valign="top">
      <b>🐳 kau/pytorch-master</b><br><br>
      <table>
        <thead><tr><th>패키지</th><th>버전</th></tr></thead>
        <tbody>
          <tr><td>torch</td><td>2.5.1</td></tr>
          <tr><td>torchvision</td><td>0.20.1</td></tr>
          <tr><td>vllm</td><td>0.6.6.post1</td></tr>
          <tr><td>accelerate</td><td>latest</td></tr>
          <tr><td>transformers</td><td>latest</td></tr>
          <tr><td>datasets</td><td>latest</td></tr>
          <tr><td>numpy</td><td>latest</td></tr>
          <tr><td>pandas</td><td>latest</td></tr>
          <tr><td>matplotlib</td><td>latest</td></tr>
          <tr><td>scipy</td><td>latest</td></tr>
          <tr><td>scikit-learn</td><td>latest</td></tr>
        </tbody>
      </table>
    </td>
    <td width="40"></td>
    <td valign="top">
      <b>🐳 kau/tensorflow-master</b><br><br>
      <table>
        <thead><tr><th>패키지</th><th>버전</th></tr></thead>
        <tbody>
          <tr><td>tensorflow</td><td>2.17.0</td></tr>
          <tr><td>numpy</td><td>1.26.4</td></tr>
          <tr><td>transformers</td><td>latest</td></tr>
          <tr><td>datasets</td><td>latest</td></tr>
          <tr><td>pandas</td><td>latest</td></tr>
          <tr><td>matplotlib</td><td>latest</td></tr>
          <tr><td>scipy</td><td>latest</td></tr>
          <tr><td>scikit-learn</td><td>latest</td></tr>
        </tbody>
      </table>
    </td>
  </tr>
</table>

**작성 규칙**

```
패키지명만 쓰면 최신 버전 설치       opencv-python
버전 고정이 필요하면 == 사용         diffusers==0.27.0
여러 개는 띄어쓰기로 구분            opencv-python diffusers==0.27.0 albumentations
```

### Step 3 — 자동 검증 (GitHub Actions)
이슈 제출 후 약 1분 이내에 자동으로 아래 항목이 검증됩니다.

- ✅ 사용자 ID 유효성 (조직 멤버 여부 확인)
- ✅ MIG 슬라이스 수 (그룹별 허용 범위 확인)

검증 결과는 **이슈 코멘트로 자동 통보**됩니다.  
검증 실패 시 사유가 코멘트로 안내되며, 수정 후 재요청할 수 있습니다.

### Step 4 — Jenkins 자동 실행
검증 통과 후 Jenkins 파이프라인이 자동으로 실행됩니다.

1. 요청된 MIG 슬라이스를 H200에 할당
2. 지정한 Docker 이미지로 컨테이너 생성
3. GitHub 레포지토리 코드 Clone
4. 지정한 명령어 실행
5. 실행 완료 후 컨테이너 및 MIG 자원 즉시 반납

### Step 5 — 결과 수령
실행이 완료되면 **이슈 코멘트**로 결과가 전달됩니다.

- 📊 학습 로그 및 메트릭 (loss, accuracy 등)
- 📄 실행 결과 리포트 (`.txt`)

> ⚠️ **결과물만 전달**되며, 컨테이너 내부 환경에는 직접 접근이 불가합니다.  
> ⚠️ 실행 결과 리포트는 **최대 65,000자**까지 제공되며, 초과분은 일부 잘리거나 출력되지 않을 수 있습니다.

---

## ⚠️ 주의사항

- 요청 전 본인의 **그룹 MIG 한도**를 반드시 확인하세요. 초과 요청은 자동 반려됩니다.
- 실행할 코드 레포지토리는 **Public이거나, 접근 가능한 Private 레포**여야 합니다.
- 컨테이너는 실행 완료 후 **즉시 삭제**됩니다. 필요한 결과물은 코드 내에서 미리 저장 처리하세요.
- 이 레포지토리는 **요청서 제출 전용**입니다. 인프라 관련 문의는 관리자에게 별도로 연락하세요.
- MIG 슬라이스를 2개 이상 요청하여 동시 사용하는 경우, 다중 GPU 학습 환경(분산 설정 등)은 사용자가 직접 코드 내에서 구성해야 합니다. 

---

## 📬 문의

인프라 관련 문의 또는 초대 요청은 [항공드론사업단](https://www.aerodrone.ac.kr/ko/support/application/rent/application/4) 페이지를 참고하세요.

---

<div align="center">
  <sub> AeroDrone Business Unit · H200 GPU Infrastructure</sub>
</div>
