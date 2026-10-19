# LangChain · LangGraph · RAG 수업 비교: modu_llm5 vs 음성 AI 부트캠프

> 비교 대상
> - **A. modu_llm5** (`/Users/greenpianorabbit/Documents/Development/modu_llm5`): 올해 상반기 LLM/AI 서비스 개발 부트캠프, 12주 과정
> - **B. 이 저장소** (ICT 혁신 스퀘어 음성 AI/딥러닝): 2026-10-19(월) 수업 `014_langchain/`, `015_langgraph/`, `016_rag/`
>
> 근거는 **두 저장소의 노트북 코드와 설명 셀**입니다. 강사님이 구두로 하신 설명은 반영하지 못했습니다.
> `016_rag/5.LangGraph_웹검색_챗봇.ipynb`는 내일(10/20) 마무리하므로 **지금 파일에 있는 부분(설정, State 정의)까지만** 근거로 썼습니다.

---

## 0. 한 장 요약: 가장 큰 차이 6가지

| # | 차이 | A. modu_llm5 | B. 음성 AI 부트캠프(이번 수업) |
|---|---|---|---|
| 1 | **RAG 체인을 만드는 방법** | **LCEL**로 직접 조립 (`retriever \| prompt \| llm`, `RunnableParallel`) | **`RetrievalQA`**(미리 짜인 체인)와 **`create_retrieval_chain`** (둘 다 `langchain_classic` 패키지) |
| 2 | **벡터 DB** | 주로 **Chroma** (디스크 저장 `persist_directory`) | **FAISS** (메모리에만 있음, 저장 안 함) |
| 3 | **웹 검색** | `Tavily` 도구 (`langchain_tavily`) | **SerpAPI를 `requests`로 직접 호출** (LangChain 도구 아님) |
| 4 | **LangGraph 안에서 LLM 호출** | LangChain `ChatOpenAI` | 016/5는 **OpenAI SDK를 직접** 호출 (LangChain 없이 LangGraph만 사용) |
| 5 | **에이전트, 메모리** | `create_agent` + 체크포인터, `InMemorySaver`/`SqliteSaver` | 에이전트 셀은 아직 비어 있고, 대화 메모리는 `InMemoryChatMessageHistory`를 **손으로** 관리 |
| 6 | **개발 환경** | `uv` + `pyproject.toml`(버전 고정), Langfuse/LangSmith 추적 | `conda`(voice-ai) + 노트북 첫 셀의 `%pip install`, 추적 도구 없음 |

핵심은 **"같은 개념을 다른 층에서 가르친다"**는 점입니다. A는 부품 하나하나(Loader → Splitter → Embedding → VectorStore → Retriever → 체인)를 해체해서 배운 뒤 조립했고, B는 **"전체 흐름을 먼저 한 번에 돌려 보는"** 쪽에 가깝습니다. (이 해석은 노트북 구성에서 읽은 것이고, 수업 방식에 대한 제 판단이 섞여 있습니다.)

---

## 1. 과정의 성격 비교

| 항목 | A. modu_llm5 | B. 음성 AI 부트캠프 |
|---|---|---|
| 규모 | 12주, 프로젝트 4개 | 이번 수업은 하루 저녁(19시~22시 50분 타임스탬프), 6개 노트북 |
| 주제 | 챗봇 → RAG 평가·Text2SQL → LangGraph 에이전트 → 문서 파싱·멀티모달 | 음성·딥러닝 과정 안에서 LLM 서비스 구성 요소를 소개 |
| LangChain 분량 | 1~3주 (프롬프트, LCEL, 문서 로더, 스플리터, 임베딩, 벡터스토어, 리트리버, 프롬프트 엔지니어링, 대화 이력) | 노트북 4개 (LC01~LC04) |
| LangGraph 분량 | 7~9주 (StateGraph, ReAct, 메모리, HITL, SubGraph, Adaptive/Self/CRAG RAG) | 노트북 2개 (LG01, LG02) + 016/5 일부 |
| RAG 분량 | 2주~ (로더, 스플리터, 임베딩, 벡터스토어, 리트리버, 평가 지표 등) | 노트북 1개 (`3.Simple_RAG`) |
| 도메인 | 주택 FAQ, ETF 추천, KTS 법률 에이전트, 10-K 보고서 등 | 자동차 카탈로그(5대, 문서 하나), 웹 검색 챗봇 |
| 과정 목표와의 연결 | LLM 서비스 개발 자체가 목표 | `LC01_강사님`의 설명: STT(Whisper) → LLM → 검색/도구 → TTS 파이프라인을 **LangChain/LangGraph로 엮는 도구**로 소개 |

(수업 시간 숫자는 노트북 맨 위 타임스탬프에서 읽은 것입니다. 실제 수업 시간은 다를 수 있습니다.)

---

## 2. LangChain 비교

### 2.1 "왜 LangChain인가"를 설명하는 방식

| | A. modu_llm5 | B. 이번 수업 |
|---|---|---|
| 출발점 | `PRJ01_W1_002`에서 OpenAI Chat Completion을 먼저 → `W1_003`에서 LangChain 컴포넌트 | `LC02`에서 **같은 문제를 API 직접 호출과 LangChain으로 나란히** 구현해 비교 |
| 설명 | 컴포넌트 단위: 모델, 메시지(Human/AI/System), 프롬프트, 체인, 에이전트 | 컴포넌트 7개 표 (PromptTemplate, ChatModel, OutputParser, Chain, Memory, Tool, Agent) + "컨베이어 벨트/도구 상자/비서" 비유 |
| 모델 제공자 | OpenAI + Google Gemini 실습 포함 | OpenAI 실습, Claude(`ChatAnthropic`)는 키가 없어 **실행 안 되는 참고 코드** |

→ 접근 순서(API 먼저, LangChain 나중)는 **같은 흐름**입니다. 다만 B가 비교를 한 노트북 안에서 바로 보여 줍니다.

### 2.2 체인(LCEL)

```python
# A, B 모두 같은 문법
chain = prompt | llm | StrOutputParser()
chain.invoke({...})
```

- 두 과정 모두 **LCEL(`|` 연산자)와 `invoke()`**를 씁니다. B의 `LC01_강사님`도 "예전 자료의 `LLMChain`, `chain.run()`은 더 이상 쓰지 않는다"고 명시합니다.
- A는 여기에 더해 `RunnableParallel`, `RunnablePassthrough`, `RunnableLambda`, `.batch()`, `.stream()`, `.astream()` 등 **Runnable 인터페이스를 따로 배웁니다** (`W1_004`).
- B는 `RunnableLambda`를 **조건 분기용**(LC/LG02에서 질문 길이로 체인을 고르는 `route`)으로만 씁니다.

### 2.3 다단계 체인

- B(`LC03`): 요약 → 번역을 `{"summary_text": summarize_chain} | translate_prompt | llm | StrOutputParser()`로 연결. 같은 일을 OpenAI SDK 함수(`call_gpt`)로 두 번 호출하는 코드와 **나란히 비교**합니다.
- A: LCEL 컴포지션 안에서 `RunnableParallel`로 여러 입력을 합치는 방식을 RAG 체인(`context`, `input`)에서 보여 줍니다 (`W2_002`).

### 2.4 대화 메모리

| | A. modu_llm5 (`W3_005`, `PRJ03_W2_004`) | B. 이번 수업 (`LC03`) |
|---|---|---|
| 방법 | `BaseChatMessageHistory` 직접 구현 → `RunnableWithMessageHistory`, SQLite 영구 저장, 메시지 트리밍(`trim_messages`), 대화 요약 저장, 그리고 `create_agent` + `InMemorySaver`/`SqliteSaver` | `MessagesPlaceholder("history")` + `InMemoryChatMessageHistory`에 **`add_user_message`/`add_ai_message`를 손으로 호출** |
| 저장 위치 | 메모리, SQLite | 메모리만 |
| 평가 | A의 노트북이 "`RunnableWithMessageHistory`는 1.0에서도 동작하지만 새 프로젝트에는 `create_agent` + checkpointer를 권장"이라고 적음 | 이 두 방식 모두 쓰지 않는 **가장 기초 형태**(원리 이해용으로 보임, 제 추정) |

### 2.5 도구와 에이전트

| | A | B |
|---|---|---|
| 도구 정의 | `@tool` + Pydantic 스키마, `handle_tool_error`, 내장 도구(Tavily 등) | `@tool`로 함수 두 개(`add_numbers`, `multiply_numbers`). LLM 없이 `.invoke({"a": 3, "b": 5})`로 단독 실행해 보는 점이 특징 |
| 에이전트 | `create_agent` (+ 미들웨어, 체크포인팅), ReAct 직접 구현, LangGraph로 에이전트 구성 | 노트북 `LC04`의 "LangChain 사용해서 agent 만들기" 아래 셀이 **지금은 비어 있음** (수업에서 어디까지 했는지는 확인 못 함) |

---

## 3. RAG 비교 (가장 차이가 큰 부분)

### 3.1 파이프라인 단계별

| 단계 | A. modu_llm5 | B. `3.Simple_RAG_자동차카탈로그` |
|---|---|---|
| 데이터 | 웹페이지(`WebBaseLoader`), 뉴스, PDF, 메뉴판 txt 등 다양 | **자동차 카탈로그 txt/PDF** (같은 내용을 두 형식으로 준비, PDF는 탭/줄바꿈을 정제하는 함수 `clean_pdf_catalog_text` 포함) |
| 로더 | `WebBaseLoader`, `PyPDFLoader`, `TextLoader` | `TextLoader`, `PyPDFLoader` |
| 분할 | `CharacterTextSplitter`로 먼저 시작하고(`W2_002`), 스플리터는 `W2_004`에서 `RecursiveCharacterTextSplitter` 중심으로 따로 다룸. chunk_size 500~1000, overlap은 10~20% 권장(`W2_002` 설명) | `RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)`, 데이터가 작아 **차량 하나 = 조각 하나(5개)** |
| 임베딩 | `OpenAIEmbeddings`(text-embedding-3-small), `HuggingFaceEmbeddings`(한국어 모델) 등 비교 | `OpenAIEmbeddings(text-embedding-3-small)` 하나 |
| 벡터 DB | **Chroma** (`persist_directory`로 디스크 저장, 컬렉션) | **FAISS** `from_documents` (메모리, 저장 단계 없음) |
| 검색기 | Top-K, 임계값, **MMR**, 메타데이터 필터, 본문 필터까지 `W2_007`에서 따로 학습 | `as_retriever(search_kwargs={"k": 3})` **하나만** |
| 체인 | **LCEL 직접 조립** (`RunnableParallel`로 `context`와 `input`을 만들고 프롬프트 → LLM → 파서) | **방식 A `RetrievalQA`** → **방식 B `create_retrieval_chain`** (프롬프트 직접 지정) |
| 응답 확인 | 체인 결과에서 `answer`, `context` | A는 `result`/`source_documents`, B는 `answer`/`context` |
| 평가 | `PRJ02`에서 **검색 지표, 생성 지표, LLM-as-Judge, 평가자 일치도**까지 (파일명 기준, 내용은 읽지 않음) | 아직 없음 (정성 확인만: "쏘나타 가격은?" 같은 카탈로그에 없는 질문에 거절하는지 확인) |

### 3.2 체인 방식 대응표 (헷갈리기 쉬움)

| 하는 일 | A (modu)의 방식 | B (이번 수업)의 방식 |
|---|---|---|
| 검색 → 프롬프트 → 생성을 한 덩어리로 | `retriever \| ...` LCEL 직접 | `RetrievalQA.from_chain_type(...)` — **`deprecated`**(소스 확인, 제거 예정 2.0.0), 기본 프롬프트가 영어 |
| 프롬프트를 내가 정하는 RAG 체인 | `ChatPromptTemplate` + LCEL | `create_stuff_documents_chain` + `create_retrieval_chain` |
| 입력/출력 키 | 체인 정의에 따라 직접 정함 | `RetrievalQA`: `query`/`result`, `create_retrieval_chain`: `input`/`answer`/`context` |
| 검색된 조각 확인 | 직접 출력 | `return_source_documents=True` 또는 `context` 키 |

- **의미 있는 점**: A에서 LCEL로 직접 짜 본 사람에게 B의 `RetrievalQA`는 "**내가 직접 조립하던 것을 클래스 하나로 묶어 둔 것**"입니다. 반대로 `retriever`와 `llm`이 두 일꾼이고 체인은 둘을 엮는 감독이라는 구조는 두 방식이 같습니다 (자세한 내부 흐름은 `3.Simple_RAG_자동차카탈로그_강사님.ipynb`의 설명 셀 참고).
- B 노트북의 `from langchain_classic.chains import RetrievalQA, create_retrieval_chain` 경로는 **A 저장소 코드에서는 한 번도 나오지 않습니다.** (A 저장소 전체 검색 결과 `RetrievalQA`, `create_retrieval_chain`, `create_stuff_documents_chain` 모두 0건)
- B 노트북은 `try: from langchain_classic... except ImportError: from langchain.chains ...`로 **LangChain 0.x와 1.x를 둘 다 지원**하는 import를 씁니다. A는 1.x(`langchain>=1.2.8`) 기준입니다.

### 3.3 "다음 수업(4번)" 예고

B의 방식 B 설명 셀에 "다음 수업(4번)에서는 체인 없이 검색 결과를 직접 프롬프트에 넣어 같은 일을 해 봅니다"라고 적혀 있습니다. 즉 B는 **"체인 → (체인 없이 직접)" 순서로 추상화를 벗겨 가는 구성**일 수 있습니다 (이 줄 외에는 4번 노트북이 아직 없어 확인 못 함).

---

## 4. LangGraph 비교

| 항목 | A. modu_llm5 | B. 이번 수업 |
|---|---|---|
| State 정의 | `TypedDict` (`PRJ03_W2_001`) | LG01·LG02는 **Pydantic `BaseModel`** (`question: str`, `answer: Optional[str]`), 016/5는 **`TypedDict(total=False)`** |
| 노드 | LLM 호출 노드(`ChatOpenAI`), 평가·분기 노드 | LG01/02는 `ChatOpenAI`, **016/5(작성 중)는 `requests` + OpenAI SDK** |
| 분기 기준 | **LLM이 판단**(예: 요약 품질을 LLM에게 물어 `good`/`needs_improvement`) | **질문 글자 수 > 20**이라는 **규칙 기반** 분기 (`classify` → `direct_answer`/`search_answer`) |
| 조건부 엣지 | `add_conditional_edges` + 라우팅 딕셔너리, `Literal` 반환 | `add_conditional_edges` + **람다 함수**로 다음 노드 이름 반환 |
| 그래프 확인 | `draw_mermaid_png()`로 **그림**, `draw_mermaid()`로 텍스트 | `draw_mermaid()` **텍스트** 출력 후 **스크린샷을 md 셀로 삽입** |
| 실행 방식 | `invoke`, `stream`(values/updates/messages/custom/debug 모드) | `invoke`만 |
| 흐름 제어 | `Command(update=..., goto=...)` | 다루지 않음(지금까지) |
| 메모리 | `InMemorySaver`, `SqliteSaver` 체크포인터, `RemoveMessage` | 아직 없음 |
| 에이전트 | ReAct, ToolNode, HITL(`interrupt`), SubGraph | 아직 없음 |
| 고급 RAG | Adaptive, Self RAG, CRAG | 아직 없음 |
| 추적 | Langfuse 콜백 핸들러 | 없음 |

- **B의 `LG02`는 "LangChain vs LangGraph" 같은 분기를 두 방식으로 구현**해 비교합니다: `RunnableLambda(route)`로 체인을 고르는 방식 vs `add_conditional_edges`로 노드를 고르는 방식. A는 LangGraph를 단독으로 배운 뒤 LangChain과 비교하는 구성은 따로 두지 않았습니다 (제가 읽은 범위에서는).
- B의 강사님 설명 셀(`LC01_강사님`)은 **"LangChain 없이도 LangGraph를 쓸 수 있다"**고 명시하고, 016/5의 구조를 "LangGraph로 흐름 관리 + OpenAI SDK로 모델 호출"이라고 설명합니다. A에서는 LangGraph 노드 안에서 LangChain 객체를 쓰는 것이 기본이었습니다.

---

## 5. 개발 환경·운영 방식 비교

| 항목 | A. modu_llm5 | B. 음성 AI 부트캠프 |
|---|---|---|
| 가상환경 | `uv` + `.venv` (`pyproject.toml`, `uv.lock`) | `conda` `voice-ai` (이 환경 하나만 사용) |
| 설치 방법 | `uv add "패키지<버전"`, 설치 전 `docs/DEPENDENCIES.md` 확인 | 노트북 첫 셀 `%pip install -U ...` (강사님 원문은 버전 고정 없음) |
| **faiss-cpu 버전** | **`<1.8`로 고정** ("1.8+는 macOS 14+ 전용"이라고 기록) | 강사님 명령은 **고정 없음** → 이 맥(macOS 13)에서는 **직접 `"faiss-cpu<1.8"`로 고쳐서 설치**함 (`개발환경_이슈노트.md` #13) |
| 같은 하드웨어 제약 | Intel Mac(macOS 13) 제약이 `CLAUDE.md`에 상세히 문서화됨 (torch, numpy<2 등) | 동일 컴퓨터. 같은 제약(numpy 1.26.4 유지 등)이 TensorFlow 2.16과도 맞물림 |
| 모델 | gpt-4.1-nano, gpt-4.1-mini, gpt-4o-mini, gpt-4.1 등 (실습마다 선택) | `MODEL = "gpt-4o-mini"` **상수 하나**로 통일 (코드 주석: 2027-01-14 종료 예정) |
| API 키 관리 | 프로젝트 루트 `.env`, `load_dotenv(override=True)` | 저장소 루트 `.env`(이번에 이동), 노트북은 `load_dotenv()` 또는 현재/상위 폴더 탐색 + `assert`/예시 문구 검사 |
| 모니터링 | LangSmith/Langfuse로 **모든 체인 추적**이 규칙 | 노트북에서는 다루지 않음 (`langsmith`는 의존성 패키지로만 설치됨) |
| 에러 처리 | 도구 오류 처리(`handle_tool_error`) 등은 심화 과정에서 | **016/5에서는 OpenAI 예외 클래스를 종류별로 import** (`AuthenticationError`, `RateLimitError`, `APITimeoutError` 등), `timeout=60`, `max_retries=2` — API 클라이언트 레벨 견고성을 일찍 다룸 |
| UI | `Gradio` 챗봇으로 서비스화 (`W1_005`, `W2_007`) | 지금까지 없음 |

---

## 6. 같은 점 (겹치는 부분)

- **LCEL**: `prompt | llm | parser` 형태와 `invoke()`
- **API 먼저, 프레임워크는 나중**: OpenAI SDK 호출을 먼저 보여 주고 LangChain이 무엇을 줄여 주는지 비교
- **RAG의 5단계**: 로드 → 분할 → 임베딩 → 벡터 DB → 검색 → 생성 (이 노트북의 설명 셀이 A의 RAG 개념 설명과 같은 구조)
- **LangGraph의 3요소**: State, Node, Edge, `START`/`END`, `compile()`, 조건부 엣지
- **임베딩 모델**: `text-embedding-3-small`
- **`RecursiveCharacterTextSplitter`, `OpenAIEmbeddings`, `FAISS`**: A에서도 쓴 적 있음 (A `W2_007` 프로젝트는 FAISS+HuggingFace 임베딩)

---

## 7. 이번 수업 내용이 A에서 배운 것과 어떻게 이어지나 (복습 지도)

| 이번 수업 | A에서 이어서 볼 노트북 |
|---|---|
| `LC01`~`LC02`: 첫 체인, API vs LangChain | `PRJ01_W1_002`, `W1_003`, `W1_004` (LCEL을 더 깊게) |
| `LC03`: 다단계 체인, 대화 메모리 | `PRJ01_W3_005_Chat_History` (영구 저장, 트리밍, 요약, 체크포인터) |
| `LC04`: Tool, Agent | `PRJ03_W1_002`~`W1_006` (`create_agent`, Tavily, 미들웨어) |
| `LG01`~`LG02`: StateGraph, 조건부 엣지 | `PRJ03_W2_001` (`Command`, `stream` 모드), `W2_003`(ReAct), `W2_004`(메모리) |
| `3.Simple_RAG`: `RetrievalQA`, `create_retrieval_chain` | `PRJ01_W2_002`~`W2_007` (같은 일을 LCEL과 Chroma로), `PRJ02_W1`(검색 지표, 하이브리드, 리랭크) |
| `5.LangGraph_웹검색_챗봇` (내일 마무리) | `PRJ03_W3_001`~(Adaptive RAG: 질문 유형에 따라 RAG vs 웹 검색 분기) — 이번 `LG02`의 "짧은 질문/긴 질문 분기"의 심화판으로 볼 수 있음 |

---

## 8. 이 비교의 한계 (이렇게 이해하세요)

1. **구두 설명은 반영하지 못했습니다.** 강사님이 말로 하신 설명이나 수업 중 시연은 노트북에 남지 않은 부분입니다.
2. **`016/5.LangGraph_웹검색_챗봇.ipynb`는 미완성**이라 지금까지의 설정, State 정의, 검색 결과 타입까지만 반영했습니다. 그래프 구성, 검색 노드, 답변 노드는 확인하지 못했습니다. 내일 마무리된 뒤 4절을 보완할 수 있습니다.
3. **`LC04`의 에이전트 부분이 비어 있어서** 이번 수업의 에이전트 방식은 비교하지 못했습니다. (`LC01_강사님`에 에이전트 설명 표만 있음)
4. **A의 모든 노트북을 읽지는 않았습니다.** 비교에 쓴 것은 `PRJ01_W1_003/004`, `W2_002/007`, `W3_005`, `PRJ03_W1_006`, `W2_001/003/004`, 각 프로젝트 `CLAUDE.md`의 요약이고, 나머지(평가, Text2SQL, Adaptive/Self/CRAG, 10-K 파싱 등)는 제목 수준으로만 반영했습니다.
5. **"B의 구성 의도"에 대한 해석**(예: 추상화를 벗겨 가는 순서, 기초 형태)은 노트북에서 읽은 **제 추정**입니다. 강사님의 실제 의도와 다를 수 있습니다.
6. 코드 동작(예: 아래 항목)은 이 저장소 환경에서 직접 확인한 것입니다: `RetrievalQA`의 deprecated 표시와 내부 호출 순서, `chain_type_kwargs`로 프롬프트 변경 가능, `create_retrieval_chain` 결과 키. A 저장소의 코드를 **실행해서** 확인한 것은 없습니다(읽기만 함).
