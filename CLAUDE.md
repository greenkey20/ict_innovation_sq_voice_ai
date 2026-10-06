# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a personal study repository of Jupyter notebooks for an ML/DL course (ICT 혁신 스퀘어), not a software application. There is no build, lint, or test tooling, no package manifest, and no git repository — everything here is notebook-based coursework plus the datasets and saved Keras models used by it.

Notebook filenames and content are in Korean. Many topics have two or three variants of the same notebook, distinguished by filename suffix:
- plain filename (e.g. `퍼셉트론.ipynb`, `DogCat_V2.0_Basic.ipynb`) — the base/working copy
- `_강사님` suffix (e.g. `경사하강법_개념실습_강사님.ipynb`) — the instructor's reference copy
- `_은영 수업` suffix (e.g. `DogCat_V2.0_Basic_은영 수업.ipynb`) — the student's own in-class worked copy
- `_Load` suffix (e.g. `DogCat_V2.0_Basic_Load.ipynb`) — a companion notebook that loads a saved model back and runs inference/evaluation, rather than training

When asked to fix or extend a notebook, prefer editing the plain or `_은영 수업` version unless the user says otherwise; treat `_강사님` notebooks as reference material to compare against, not to modify. `Untitled.ipynb` is scratch space, not part of any course sequence.

## Environment

- No requirements/environment file exists. **This course uses only the `voice-ai` conda environment (Python 3.11, at `/opt/anaconda3/envs/voice-ai`)** — other envs on this machine (`base`/`conda-base-py` Python 3.13, `tf_env`, `study`) are unrelated to this course and should not be used for it, even though some older notebooks here predate that convention and were authored against `base`. Check which kernel a notebook is actually using (`import sys; print(sys.executable)`) before assuming a package is (or isn't) installed.
- Ongoing setup problems, root causes, and fixes for this course's environment are logged in `개발환경_이슈노트.md` — check it first when a package/import/install issue looks familiar, and add new issues there (not here) as they come up.
- **Kernel/shell mismatch gotcha:** `!pip install X` inside a notebook cell runs in the shell environment that launched Jupyter (often `base`), which can silently differ from the notebook's actual kernel (e.g. `voice-ai`). If `import X` fails right after a successful-looking `!pip install X`, don't just restart the kernel — first check `import sys; print(sys.executable)` to confirm which env the kernel is really using, and install with `!{sys.executable} -m pip install X` to guarantee it lands in the right place.
- When a `pip install` of a package with compiled extensions (e.g. `opencv-python`) looks like it's building from source (`Downloading ...tar.gz` + `Building wheels for collected packages`) rather than pulling a `.whl`, it means no prebuilt wheel matches the current Python version — expect a long (or failing) build. Prefer pinning a version known to ship wheels (e.g. `opencv-python-headless==4.9.0.80`) or creating a fresh conda env for that Python version rather than waiting out a source build.
- `conda install` run from a notebook cell needs `-y` (no interactive prompt support) and can be very slow to solve against the heavyweight `base` env, especially mixing the `defaults` and `conda-forge` channels; a dedicated `conda create -n <name> ...` env solves much faster than installing into `base`.
- `mat_kor.py` is a shared helper imported by several notebooks as `import mat_kor` (not `import mat_kor.py`) to configure Matplotlib for Korean text: it sets `AppleGothic` on macOS, `Malgun Gothic` on Windows, `NanumGothic` on Linux, and disables unicode minus-sign rendering. Keep this import pattern when a notebook plots Korean labels.
- Running notebooks: `jupyter notebook` or `jupyter lab` from the repo root (so relative paths to `dataset/`, `model/`, `No_Img/`, `model1006/` resolve, and so `import mat_kor` works).

## Data and model artifacts

- `dataset/` holds the CSVs/UCI data used across notebooks: `housing.csv` (Boston housing regression), `pima-indians-diabetes.csv`, `sonar.csv`, `wine.csv`, `iris.csv`/`iris/`, `data-03-diabetes.csv`, `ThoraricSurgery.csv`, `Blood_fat.csv`, `HealthProductAd.csv`. Notebooks load these via relative paths (e.g. `pd.read_csv('dataset/housing.csv')`), so keep working directory assumptions in mind when running cells.
- `model/` holds saved Keras checkpoints, named `<epoch>-<val_loss>.keras` (e.g. `model/235-0.1404.keras`), produced by `ModelCheckpoint` callbacks during training notebooks (`Housing_선형회귀_자동중단_모델 코드.ipynb`, `best model 만들기.ipynb`, `과적합 피하기 및 모델 저장.ipynb`). `model/best/` holds the best-performing checkpoints singled out from a run. `model1006/` is the same pattern (`<epoch>-<val_loss>.keras`) for a separate, later training run (the `mnist_검증_basic.ipynb` notebook). Top-level `my_model.keras` and `model/housing_1001*.keras` are final saved models loaded back via `load_model(...)` in the corresponding `*_load model.ipynb` / `모델 불러오기.ipynb` notebooks.
- Top-level `Model_DNN_NoGen_*.keras` files (e.g. `Model_DNN_NoGen_은영.keras`, `Model_DNN_NoGen_강사님.keras`) are independent, full training runs of the same `DogCat_V2.0_Basic*` DNN architecture by different people — same code/architecture, different learned weights. Don't assume files sharing a base name are interchangeable; compare them (e.g. evaluate both against `dataset/dogvscat_data/Test`) rather than assuming parity. `Model_DNN_NoGen_비교.md` documents one such comparison and the root-cause analysis for why two runs of identical code diverged (unseeded randomness in a flatten-based DNN with aggressive early stopping) — follow that pattern (seed check, data-balance check, then direct evaluation) if asked to compare other model variants.
- `No_Img/` holds a handful of ad-hoc single-digit images (e.g. `3.png`, `5.jpg`, `7.jpg`) used as manual inference inputs by `mnist_검증_basic.ipynb` — note the inconsistent extensions; a notebook hardcoding `.jpg` for a file that's actually `.png` will fail silently via `cv2.imread` returning `None`.
- Do not delete files under `model/`, `model1006/`, `dataset/`, or top-level `*.keras` files without confirming — they are training outputs and inputs other notebooks depend on, and checkpoints are not reproducible without rerunning training (which can take a while).

## Notebook progression (rough topic order)

1. `01_01`/`01_02` — NumPy array basics
2. `26_3_01` … `26_3_06` — core Python syntax (print/types, if, sequences, while/for loops, functions)
3. `03_01 시각화 패키지 Matplotlib 소개` — Matplotlib plotting, using `mat_kor`
4. `경사하강법*` — gradient descent from first principles, then with TF1-style (`tensorflow.compat.v1`) and TF2/Keras APIs
5. `퍼셉트론`, `로지스틱 회귀`, `선형회귀 실습`, `file로부터의 다중선형 회귀 실습` — perceptron and regression fundamentals
6. `Keras code`, `Keras 선형 회귀 실습`, `Housing_선형회귀_자동중단_모델 코드*`, `Boston 집값 예측*` — Keras `Sequential` models with `Dense`/`Input` layers, `train_test_split`, `EarlyStopping`/`ModelCheckpoint`, and reloading saved models
7. `pima-indians`, `다중 분류 문제 해결하기 및 과적합 피하기`, `과적합 피하기 및 모델 저장`, `best model 만들기*` — classification, multi-class problems, overfitting mitigation, checkpointing best models
8. `비지도 학습` — unsupervised learning (clustering, via `sklearn.datasets`)
9. `mnist_basic`, `mnist_검증_basic` — MNIST digit classification with Keras, including manual inference against hand-made images in `No_Img/` via `cv2`
10. `DogCat_V2.0_Basic*` — cat/dog binary image classification with a flatten-based DNN (`Dense(512)→Dropout→Dense(256)→Dropout→Dense(1, sigmoid)`), trained on `dataset/dogvscat_data/`, with `_Load` variants for reloading and evaluating saved models

When editing one notebook in a pair (plain vs `_강사님`) or a notebook that reuses a pattern from an earlier one in this sequence, check the earlier notebook for the established style (e.g. how `mat_kor` is imported, how `train_test_split`/`ModelCheckpoint` are configured) rather than introducing a new pattern.
