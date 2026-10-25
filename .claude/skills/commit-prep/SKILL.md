---
name: commit-prep
description: 커밋준비 (/커밋준비). git commit 전에 체크리스트(.gitignore 대상, 노트북에 임베드된 내 목소리 음원·경로, _강사님 파일, 비밀값)를 점검하고 이 저장소 컨벤션의 커밋 메시지 초안을 제안한다. 사용자가 승인하면 git add + commit을 실행한다(Co-Authored-By 없이). "커밋 준비", "커밋 전에 점검", "커밋해도 되는지 확인" 같은 요청에 사용.
---

# 커밋 준비 (체크리스트 + 커밋 메시지 초안)

이 저장소는 **공개 GitHub 저장소**이고, 노트북 출력에 내 목소리 음원(base64)이나 컴퓨터 경로가 들어가기 쉽다. 커밋 전에 아래를 점검하고, **사용자가 승인한 뒤에만** 커밋한다(CLAUDE.md: 커밋·push는 명시적 확인 후).

## 지켜야 할 컨벤션 (CLAUDE.md·git 이력 요약)

- 커밋은 **주제별로 나눈다**(한 커밋에 노트북 내용, 설정, 문서를 섞지 않는다).
- **메시지 접두어**: `feat:`(새 노트북·새 기능·실습 추가), `docs:`(설명·노트·리뷰·CLAUDE.md·README 갱신), `chore:`(`.gitignore`·설정 정리). 접두어 뒤에 **한글 설명**을 쓴다. 예: `docs: 017 02 노트북에 10/22 수업(리샘플링·자르기) 내용과 설명 추가`.
- **Co-Authored-By 줄을 넣지 않는다**(사용자 지시). 이 스킬로 만드는 커밋 메시지에는 어떤 `Co-Authored-By` 줄이나 "Generated with" 문구도 붙이지 않는다.
- 파일은 **하나씩 이름을 지정해서** `git add`한다(`git add .`/`-A` 금지).
- push는 이 스킬의 범위가 아니다. 사용자가 따로 "push해줘"라고 할 때만 한다.
- Jupyter/VS Code가 kernelspec 등 **메타데이터만** 바꾼 노트북은 내용 커밋과 섞지 않는다.
- `_강사님` 파일은 강사님 원본 그대로여야 한다(수정이 있으면 의도한 것인지 사용자에게 확인).

## 수행 순서

### 1. 상태 확인
```bash
git status -sb
git diff --stat
git log --oneline -5      # 최근 메시지 스타일 확인
```
수정/삭제/새 파일(untracked)을 구분해서 사용자에게 짧게 요약한다.

### 2. .gitignore 대상이 staged에 없는지 확인
```bash
git diff --cached --name-only
git ls-files -ci --exclude-standard                     # 이미 추적 중인데 ignore 규칙에 걸리는 파일
git diff --cached --name-only | xargs -I{} git check-ignore --no-index -v {} 2>/dev/null   # staged 중 ignore 규칙에 걸리는 파일
```
특히 다음이 올라가려 하면 **중단하고 알린다**: `017_sound/data/`, `017_sound/results/`(내 목소리 녹음·캡처), 저장소 루트 `.env`(API 키), `models/`·`*.keras`, `dataset/aclImdb/`·`dataset/glove.6B/`, `*.weights`·`*.pt`, `.vscode/`, `.claude/settings.local.json`. 100MB가 넘는 파일은 pre-commit 훅이 막는다.

### 3. 노트북 출력 점검 (내 목소리·경로·오류)
작업 폴더 기준과 staged 기준을 둘 다 본다. 스크립트는 읽기 전용이다.
```bash
/opt/anaconda3/envs/voice-ai/bin/python .claude/skills/commit-prep/scan_notebook_outputs.py            # 수정/새 노트북
/opt/anaconda3/envs/voice-ai/bin/python .claude/skills/commit-prep/scan_notebook_outputs.py --staged   # staged 노트북
```
스크립트가 알려 주는 것과 **경고 방식**:
- **오디오 재생기(`audio/wav` base64)**: 내 목소리·강사님 목소리가 파일에 통째로 들어 있어 **공개 저장소에서 누구나 들을 수 있다.** 셀 소스에 `my_voice`·`VOICE_PATH`·`drafts` 등이 있으면 "목소리/녹음 의심"으로 크게 경고한다. 합성음(`tone_sequence`·`make_tone`)만이면 개인정보 문제는 아니지만 파일이 커진다(GitHub 노트북 뷰어는 어차피 재생하지 못함).
- **개인 경로(`/Users/...`)·사용자 이름**이 출력에 있으면 경고한다.
- **오류 출력**, **2MB 이상**, **메타데이터만 바뀐 파일**, **`_강사님` 파일 변경/새 파일**도 표시한다(새 `_강사님` 파일에 강사님 목소리 재생기가 있을 수 있음).
- 비밀값은 별도로 확인한다: 변경 파일에서 `sk-`로 시작하는 키, `API_KEY = "..."` 같은 값이 보이면 중단한다.
  ```bash
  grep -nE "sk-[A-Za-z0-9]{16,}|(OPENAI|ANTHROPIC|SERPAPI)[A-Z_]*KEY *= *['\"A-Za-z0-9]" <변경 파일들>
  ```

경고가 있으면 사용자에게 **선택지**를 준다(승인 없이 실행하지 않는다).
- (a) 사용자가 직접 Clear Outputs(또는 목소리 셀의 출력만 삭제) 후 다시 점검한다.
- (b) **로컬 파일은 그대로 두고 커밋본에서만 제거**한다. 방법: 출력에서 오디오 재생기와 경로 줄만 뺀 사본을 임시 파일로 만들고, 그 내용을 git index에만 올린다.
  ```bash
  sha=$(git hash-object -w /private/tmp/<사본>.ipynb)
  git update-index --add --cacheinfo 100644,$sha,"<노트북 경로>"
  ```
  이렇게 하면 내 컴퓨터의 노트북(재생기 있음)은 바뀌지 않아 `git status`에는 계속 "수정됨"으로 보인다. 사본을 만든 뒤 `grep -c "audio/wav"`와 `grep -c "greenpianorabbit"`가 0인지 확인한다.

### 4. 커밋 메시지 초안 제안
- 변경 내용을 **주제별로 묶어** 커밋 단위를 정하고(예: `.gitignore` / 노트북별 / `CLAUDE.md`·README 문서), 각 단위에 파일 목록과 메시지 초안을 표로 보여 준다.
- 메시지는 `feat:`/`docs:`/`chore:` + 한글 한 줄 요약(필요하면 본문 한두 줄). 노트북 변경은 **무엇을 배웠는지/무엇을 설명했는지**를 한 줄에 담는다. 날짜(수업일)나 노트북 번호를 넣으면 이력을 읽기 쉽다.
- 이 단계에서는 아무것도 실행하지 않는다.

### 5. 승인 후 실행
사용자가 승인하면(예: "네, 커밋해줘"):
```bash
git add "<파일1>" "<파일2>"           # 커밋 단위별로, 파일 이름을 지정
git commit -q -m "<접두어>: <한글 설명>"   # Co-Authored-By 줄 없이
```
- 3의 (b)를 승인받았다면 해당 노트북은 `git add` 대신 `git update-index --cacheinfo`로 올린 상태로 커밋한다.
- 커밋 후 `git log --oneline -N`과 `git status -s`를 보여 주고, 올라간 노트북에 `audio/wav`·`greenpianorabbit`가 없는지 `git show HEAD~k:<경로> | grep -c ...`로 다시 확인한다.
- **push는 하지 않는다.** "push도 할까요?"라고 묻기만 하고, 사용자가 요청하면 별도로 `git push`를 실행한다.

## 하지 말 것

- `git add .`/`git add -A`, `--no-verify`, `git push --force`.
- 사용자 승인 없이 커밋하거나 노트북 출력을 지우기.
- `.env`·API 키·`data/`·`results/` 파일을 add하기.
