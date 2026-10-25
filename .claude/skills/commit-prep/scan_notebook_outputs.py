"""커밋 전 노트북 출력 점검 (읽기 전용, 파일을 수정하지 않음).

사용법 (저장소 루트에서):
  /opt/anaconda3/envs/voice-ai/bin/python .claude/skills/commit-prep/scan_notebook_outputs.py            # 수정/새 노트북(작업 폴더 기준)
  /opt/anaconda3/envs/voice-ai/bin/python .claude/skills/commit-prep/scan_notebook_outputs.py --staged   # staged 노트북(index에 올라간 내용 기준)
  /opt/anaconda3/envs/voice-ai/bin/python .claude/skills/commit-prep/scan_notebook_outputs.py a.ipynb b.ipynb

점검 항목: 오디오 재생기(base64 음원), 개인 경로(/Users/...), 오류 출력, 파일 크기,
          메타데이터만 바뀐 노트북, _강사님 파일 변경 여부.
"""
import json
import subprocess
import sys

# 셀 소스에 이 단어가 있으면 "내 목소리/실제 녹음"일 가능성이 높은 재생기로 표시
VOICE_HINTS = ("my_voice", "VOICE_PATH", "voice", "drafts", "record", "녹음", "강사님")
SYNTH_HINTS = ("tone_sequence", "make_tone", "np.sin", "np.zeros", "sequence", "alarm", "clean", "noisy")


def git(*args, check=True):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=check).stdout


def target_paths(argv):
    files = [a for a in argv if not a.startswith("--")]
    if files:
        return files, False
    staged = "--staged" in argv
    if staged:
        names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0")
    else:
        names = []
        for line in git("status", "--porcelain", "-z", "--untracked-files=all").split("\0"):
            if len(line) > 3:
                names.append(line[3:])
    return [n for n in names if n.endswith(".ipynb")], staged


def load(path, staged):
    if staged:
        raw = git("show", f":{path}")
    else:
        raw = open(path, encoding="utf-8").read()
    return raw, json.loads(raw)


def head_cells(path):
    try:
        return json.loads(git("show", f"HEAD:{path}"))
    except Exception:
        return None


def scan(path, staged):
    raw, nb = load(path, staged)
    audio, paths, errors = [], [], []
    for i, c in enumerate(nb["cells"]):
        src = "".join(c["source"])
        for o in c.get("outputs", []):
            d = o.get("data", {})
            if "audio/wav" in "".join(d.get("text/html", [])) or "audio/" in "".join(d.keys()):
                voice = any(h in src for h in VOICE_HINTS)
                synth = any(h in src for h in SYNTH_HINTS)
                audio.append((i, "목소리/녹음 의심" if voice and not synth else ("합성음 추정" if synth else "불명")))
            if o["output_type"] == "error":
                errors.append((i, o.get("ename")))
            if "/Users/" in json.dumps(o, ensure_ascii=False):
                paths.append(i)
    head = head_cells(path)
    meta_only = bool(head) and head.get("cells") == nb.get("cells") and head.get("metadata") != nb.get("metadata")
    return {
        "path": path,
        "cells": len(nb["cells"]),
        "mb": round(len(raw.encode("utf-8")) / 1e6, 2),
        "audio": audio,
        "paths": paths,
        "errors": errors,
        "username_hits": raw.count("greenpianorabbit"),
        "meta_only": meta_only,
        "instructor": "강사님" in path,
        "is_new": head is None,
    }


def main():
    paths, staged = target_paths(sys.argv[1:])
    if not paths:
        print("점검할 노트북이 없습니다.")
        return
    print(f"점검 대상 {len(paths)}개 ({'staged(index) 기준' if staged else '작업 폴더 기준'})")
    for p in paths:
        r = scan(p, staged)
        flags = []
        if r["audio"]:
            voice = [a for a in r["audio"] if a[1] == "목소리/녹음 의심"]
            flags.append(f"오디오 재생기 {len(r['audio'])}개 (목소리/녹음 의심 {len(voice)}개) 셀 {[a[0] for a in r['audio']][:12]}")
        if r["paths"] or r["username_hits"]:
            flags.append(f"개인 경로/사용자 이름 노출 (출력 셀 {r['paths']}, 'greenpianorabbit' {r['username_hits']}회)")
        if r["errors"]:
            flags.append(f"오류 출력 {len(r['errors'])}개 셀 {[e[0] for e in r['errors']]}")
        if r["mb"] >= 2:
            flags.append(f"크기 {r['mb']} MB (출력 때문에 큰 편)")
        if r["meta_only"]:
            flags.append("메타데이터(kernelspec 등)만 바뀜 → 내용 커밋과 섞지 말 것")
        if r["instructor"]:
            flags.append("_강사님 파일: 원본 그대로여야 함" + (" / 새 파일(강사님 목소리 재생기 여부 확인)" if r["is_new"] else " / 수정됨 → 의도한 것인지 확인"))
        print(f"- {p}  [{r['cells']}셀, {r['mb']} MB]")
        print("   " + ("이상 없음" if not flags else "\n   ".join("⚠ " + f for f in flags)))


if __name__ == "__main__":
    main()
