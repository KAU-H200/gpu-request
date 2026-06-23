# 🖥️ Aerodrone-H200 GPU 사용 요청

> **[Aerodrone-H200](https://github.com/Aerodrone-H200) · GPU Infrastructure**  
> NVIDIA H200 클러스터에서 코드를 실행하기 위한 공개 요청 레포지토리입니다.

---

## 🚨 가장 먼저 — 항공드론사업단에서 사용 신청부터 하세요

> ### ⚠️ 이슈를 작성하기 전에, 반드시 [항공드론사업단 신청 페이지](https://www.aerodrone.ac.kr/ko/support/application/rent/application/4)에서 먼저 사용 신청을 해야 합니다.
> 최소 하루전에는 신청을 해주시길 바랍니다.
>
> **본 레포지토리에서 바로 이슈를 작성할 수 없습니다.**  
> 사용 시간 신청 → 승인 → 초대 수락(1회만 진행)을 거친 후에만 요청서(이슈)를 작성할 수 있습니다.
>
> ### ⏰ 신청 시 사용 시간(기간)을 반드시 지정해야 합니다.
> 신청서에 **사용 시작·종료 시간을 명시**해야 하며, **승인된 시간 내에서만** 해당 이슈작성을 통해 GPU를 사용할 수 있습니다.  
> 지정한 시간 종료 30분전까지 계속 이슈작성을 통해 결과를 요청 할 수 있으며, 시간 외 요청은 처리되지 않습니다.

**신청 순서**

```
① 항공드론사업단 신청 페이지에서 사용 신청 (필수 선행)
        ↓
② 관리자 승인 후 Organization 초대 이메일 수신 · 수락
        ↓
③ 본 레포지토리에서 이슈(요청서) 작성
        ↓
④ 자동 파이프라인이 H200에서 실행 → 결과 반환
```

> 👉 신청 바로가기: **<https://www.aerodrone.ac.kr/ko/support/application/rent/application/4>**

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
| **Admins** | 시스템 관리자 | 7개(GPU 1개) | 전체 관리 및 설정 |
| **Maintainers** | 운영 담당자 및 교수님 | 7개(GPU 1개) | 이슈 승인 및 파이프라인 제어 |
| **Developers** | 석사 연구원 | 7개(GPU 1개) | 요청서 작성 및 코드 실행 |
| **Guests** | 학사 과정 학생 및 수업 사용 | 1개 | 결과 조회 및 제한적 요청 |

> 그룹은 GitHub Organization의 Teams 기능으로 관리됩니다.  
> **초대는 관리자(Admins)가 수행**하며, [항공드론사업단 신청](https://www.aerodrone.ac.kr/ko/support/application/rent/application/4)이 승인된 후 발송됩니다. 초대 이메일을 수락한 후 이슈를 작성할 수 있습니다.

---

## 🧩 GPU 할당량(`1` vs `7`) 이해하기
 
H200은 **두 종류의 풀**로 나뉘어 운영됩니다. 요청 시 `1` 또는 `7` 중 하나를 입력합니다.
 
| 입력값 | 실제 할당 | 메모리 | 용도 |
|:------:|----------|:------:|------|
| **`1`** | MIG 슬라이스 1개 | 약 18GB | 작은 학습 · 추론 · 실습 |
| **`7`** | **GPU 1장 통째 (물리 GPU 1개 전체)** | 약 141GB | 대형 모델 학습 · 분산 학습 · 대용량 메모리 작업 |

### ⚠️ `7`은 슬라이스 7개가 아닙니다
 
`7`은 **"물리 GPU 1장을 통째로 빌리는 것"** 을 의미합니다. MIG로 쪼갠 슬라이스 7개가 아닙니다.

> 🔔 **변경 안내:** 이제 최대 대여량은 **GPU 1장**입니다. `1`(슬라이스 1개) 또는 `7`(GPU 1장 통째) 중에서만 선택할 수 있으며, **GPU 2장 동시 대여는 더 이상 지원되지 않습니다.**


## 🚀 사용 절차

### Step 1 — 항공드론사업단 사용 신청 (필수 선행)
[항공드론사업단 신청 페이지](https://www.aerodrone.ac.kr/ko/support/application/rent/application/4)에서 H200 사용 신청을 먼저 진행합니다. **이 단계 없이는 이슈를 작성할 수 없습니다.**

신청 시 **사용 시간(시작·종료 시간 또는 기간)을 반드시 지정**해야 하며, **승인된 시간 내에서만** 코드 실행 요청이 가능합니다. 지정한 시간이 지나면 자원이 자동 회수되어 시간 외 요청은 처리되지 않습니다.

### Step 2 — 이슈 작성
상단 **Issues** 탭 → **New issue** → **컨테이너 생성 및 코드 실행 요청** 템플릿 선택

아래 항목을 모두 정확히 입력합니다.

| 항목 | 설명 | 예시 |
|------|------|------|
| 사용자 ID | 본인의 GitHub Username | `kau-student01` |
| GitHub 링크 | 실행할 코드 레포지토리 주소 | `https://github.com/username/repo.git` |
| 실행 명령어 | 코드 시작 명령어 | `python main.py` |
| 사용 이미지 | Docker 이미지 선택 | `kau/pytorch-master` |
| 사용 언어 | Python / Bash | `Python` |
| GPU 할당량 | `1`(슬라이스 1개) 또는 `7`(GPU 1장 통째) | `1` |

#### 📦 추가 필요 모듈 작성 방법
 
기본 이미지(`kau/pytorch-master`, `kau/tensorflow-master`)에 포함되지 않은 패키지가 필요할 경우에만 작성합니다.
 
아래 패키지는 **이미 설치되어 있으므로 입력 불필요**합니다.
 
<table>
  <tr>
    <td valign="top">
      <b>🐳 kau/pytorch-master</b><br>
      <sub>CUDA 13.0 기반</sub><br><br>
      <table>
        <thead><tr><th>패키지</th><th>버전</th></tr></thead>
        <tbody>
          <tr><td>torch</td><td>2.11.0</td></tr>
          <tr><td>torchvision</td><td>0.26.0</td></tr>
          <tr><td>torchaudio</td><td>2.11.0</td></tr>
          <tr><td>triton</td><td>3.6.0</td></tr>
          <tr><td>vllm</td><td>0.22.0</td></tr>
          <tr><td>transformers</td><td>5.10.1</td></tr>
          <tr><td>accelerate</td><td>1.13.0</td></tr>
          <tr><td>datasets</td><td>4.8.5</td></tr>
          <tr><td>tokenizers</td><td>0.22.2</td></tr>
          <tr><td>safetensors</td><td>0.7.0</td></tr>
          <tr><td>huggingface_hub</td><td>1.17.0</td></tr>
          <tr><td>numpy</td><td>2.2.6</td></tr>
          <tr><td>pandas</td><td>2.3.3</td></tr>
          <tr><td>scipy</td><td>1.15.3</td></tr>
          <tr><td>scikit-learn</td><td>1.7.2</td></tr>
          <tr><td>matplotlib</td><td>3.10.9</td></tr>
          <tr><td>pillow</td><td>12.2.0</td></tr>
          <tr><td>opencv-python-headless</td><td>4.13.0.92</td></tr>
        </tbody>
      </table>
    </td>
    <td width="40"></td>
    <td valign="top">
      <b>🐳 kau/tensorflow-master</b><br>
      <sub>CUDA 12.5 기반</sub><br><br>
      <table>
        <thead><tr><th>패키지</th><th>버전</th></tr></thead>
        <tbody>
          <tr><td>tensorflow</td><td>2.21.0</td></tr>
          <tr><td>keras</td><td>3.12.2</td></tr>
          <tr><td>transformers</td><td>5.10.1</td></tr>
          <tr><td>datasets</td><td>4.8.5</td></tr>
          <tr><td>tokenizers</td><td>0.22.2</td></tr>
          <tr><td>safetensors</td><td>0.7.0</td></tr>
          <tr><td>huggingface_hub</td><td>1.17.0</td></tr>
          <tr><td>numpy</td><td>2.2.6</td></tr>
          <tr><td>pandas</td><td>2.3.3</td></tr>
          <tr><td>scipy</td><td>1.15.3</td></tr>
          <tr><td>scikit-learn</td><td>1.7.2</td></tr>
          <tr><td>matplotlib</td><td>3.10.9</td></tr>
          <tr><td>pillow</td><td>12.2.0</td></tr>
          <tr><td>h5py</td><td>3.14.0</td></tr>
        </tbody>
      </table>
    </td>
  </tr>
</table>

> ⚠️ 위 버전은 기본 이미지 기준이며, 이미지 업데이트 시 변경될 수 있습니다.
> 특히 `torch` · `torchvision` · `tensorflow` 를 다른 버전으로 강제 업그레이드(`--upgrade`)하면
> CUDA 및 의존성 충돌이 발생할 수 있으니, 꼭 필요한 경우가 아니면 기본 버전을 그대로 사용하세요.

**작성 규칙**

```
패키지명만 쓰면 최신 버전 설치       opencv-python
버전 고정이 필요하면 == 사용         diffusers==0.27.0
여러 개는 띄어쓰기로 구분            opencv-python diffusers==0.27.0 albumentations
```

### Step 4 — 자동 검증 (GitHub Actions)
이슈 제출 후 약 1분 이내에 자동으로 아래 항목이 검증됩니다.

- ✅ 사용자 ID 유효성 (조직 멤버 여부 확인)
- ✅ MIG 슬라이스 수 (그룹별 허용 범위 확인)

검증 결과는 **이슈 코멘트로 자동 통보**됩니다.  
검증 실패 시 사유가 코멘트로 안내되며, 수정 후 재요청할 수 있습니다.

### Step 5 — Jenkins 자동 실행
검증 통과 후 Jenkins 파이프라인이 자동으로 실행됩니다.

1. 요청된 MIG 슬라이스를 H200에 할당
2. 지정한 Docker 이미지로 컨테이너 생성
3. GitHub 레포지토리 코드 Clone
4. 지정한 명령어 실행
5. 실행 완료 후 컨테이너 및 MIG 자원 즉시 반납

### Step 6 — 결과 수령
실행이 완료되면 **이슈 코멘트**로 결과가 전달됩니다.

- 📊 학습 로그 및 메트릭 (loss, accuracy 등)
- 📄 실행 결과 리포트 (`.txt`)

> ⚠️ **결과물만 전달**되며, 컨테이너 내부 환경에는 직접 접근이 불가합니다.  
> ⚠️ 실행 결과 리포트는 **최대 65,000자**까지 제공되며, 초과분은 일부 잘리거나 출력되지 않을 수 있습니다.

---

## ⚠️ 주의사항
 
- 이슈 작성 전 **[항공드론사업단 신청](https://www.aerodrone.ac.kr/ko/support/application/rent/application/4)이 완료·승인**되어 있어야 합니다.
- 신청 시 **사용 시간을 지정**해야 하며, **승인된 시간 내에서만** GPU 사용이 가능합니다. 시간 종료 후에는 자원이 자동 회수됩니다.
- 요청 전 본인의 **그룹 GPU 한도**를 반드시 확인하세요. 초과 요청은 자동 반려됩니다. (최대 대여량은 **GPU 1장**입니다.)
- 실행할 코드 레포지토리는 **Public이거나, 접근 가능한 Private 레포**여야 합니다.
- 컨테이너는 실행 완료 후 **즉시 삭제**됩니다. 필요한 결과물은 코드 내에서 미리 저장 처리하세요.
- 이 레포지토리는 **요청서 제출 전용**입니다. 인프라 관련 문의는 관리자에게 별도로 연락하세요.
  
---
 
## 📬 문의
 
사용 신청 · 초대 요청 · 인프라 관련 문의는 [항공드론사업단](https://www.aerodrone.ac.kr/ko/support/application/rent/application/4) 페이지를 참고하세요.
 
---
 
<div align="center">
  <sub> Aerodrone-H200 · H200 GPU Infrastructure</sub>
</div>
