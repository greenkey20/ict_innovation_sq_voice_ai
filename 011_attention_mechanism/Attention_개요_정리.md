# Attention Mechanism 개요 정리 (2026.10.14 수업 후)

RNN/LSTM → Seq2Seq → Attention으로 이어지는 흐름에서, "누가 왜 이 아이디어를 냈나"와 수업 이해 내용에 대한 피드백을 정리한다.

---

## 1. 내 정리에 대한 피드백

> 내 정리: "seq2seq에서도 입력 데이터 길이가 길어지면 컨텍스트 벡터가 이를 정확히 반영하지 못해서 디코더가 좋은 output을 내기 어려웠다 → attention mechanism에서는 decoder의 hidden state와 encoder의 hidden state의 연관도를 dot product로 계산하고, 이를 context vector 생성 시 가중치로 사용한다."

**결론: 큰 줄기는 정확하다.** 아래 네 가지를 보태면 더 정확해진다.

### 맞은 부분
- **문제 인식**: 입력이 길어져도 컨텍스트 벡터는 고정 크기(예: 128)라서 정보가 손실되는 **병목(bottleneck)** 이 생긴다. 이것이 attention이 나온 핵심 동기다.
- **해결 방향**: 디코더의 hidden state와 인코더의 hidden state가 **얼마나 관련 있는지(연관도)** 를 계산하고, 그 값을 **가중치**로 써서 컨텍스트 벡터를 만든다.

### 보태면 좋은 부분

**(1) 연관도가 바로 가중치가 되는 게 아니라, softmax를 거친다.**
```
① 점수(score)   : 인코더의 각 시점 hidden state와 디코더 hidden state의 내적(dot product)
② 가중치        : 점수들에 softmax를 적용 → 합이 1인 확률 (attention weights)
③ 컨텍스트 벡터 : 인코더 hidden state들을 그 가중치로 가중합(weighted sum)
```
예) 점수가 `[2.0, 1.0, 0.1]`이면 softmax 후 약 `[0.66, 0.24, 0.10]`이다. 인코더 3번째까지의 hidden state 중 첫 번째에 66%를 두고 합친 벡터가 컨텍스트 벡터가 된다.
→ 내 문장의 "가중치로 사용한다"는 정확히는 **"softmax로 정규화한 가중치로 인코더 hidden state들을 가중합한다"** 이다.

**(2) 컨텍스트 벡터가 "하나"에서 "출력할 때마다 새로 만드는 것"으로 바뀐다.**
- 기존 Seq2Seq: 인코더 마지막 (h, c) 하나를 **모든 출력 단계가 공통으로** 쓴다.
- Attention: 디코더가 **출력 한 칸을 만들 때마다** 컨텍스트 벡터를 새로 계산한다. 첫 단어를 낼 때는 입력의 이쪽을, 다음 단어를 낼 때는 저쪽을 더 본다.
- 이것이 "병목을 풀었다"의 실제 의미다: 입력 전체를 128차원 하나에 욱여넣지 않고, **필요할 때 입력의 해당 위치를 직접 다시 본다.**

**(3) 인코더는 마지막 상태뿐 아니라 "모든 시점의 hidden state"를 넘겨야 한다.**
- 우리 노트북(`5_숫자거꾸로_5개_모델_Seq2Seq`)의 인코더는 `LSTM(128, return_state=True)`로 **마지막 (h, c)만** 쓰고 `encoder_outputs`는 버린다.
- Attention을 쓰려면 인코더가 `return_sequences=True`로 **시점별 hidden state 전부**를 내줘야 한다. 그래야 디코더가 "어느 위치를 볼까"를 고를 수 있다. (앞서 정리한 `return_sequences`의 역할이 여기서 다시 쓰인다.)

**(4) "dot product"는 여러 방식 중 하나다.**
- 연관도(점수)를 계산하는 방법이 논문마다 다르다.
  - **Bahdanau (2014)**: 작은 신경망(MLP)으로 점수를 계산 → *additive attention*
  - **Luong (2015)**: 내적(dot) 등으로 계산 → *multiplicative attention*
  - **Transformer (2017)**: 내적을 √(차원 수)로 나눈 *scaled dot-product attention*
- 수업에서 dot product로 설명하셨다면 Luong 방식 또는 Transformer의 방식에 가깝다. 그래서 내 정리는 "Attention 중 dot-product 방식" 이라고 쓰면 정확하다.
- 참고: Bahdanau 방식은 **직전** 디코더 상태를, Luong 방식은 **현재** 디코더 상태를 점수 계산에 쓰는 차이도 있다. (세부는 논문 참고)

### 내 정리를 다듬은 버전
> Seq2Seq는 인코더가 입력 전체를 고정 크기의 컨텍스트 벡터 하나로 압축해 디코더에 넘기므로, 입력이 길어지면 정보가 손실(병목)되어 디코더의 출력 품질이 떨어졌다. Attention은 디코더가 출력을 한 칸 만들 때마다, 디코더의 현재 hidden state와 인코더의 **모든 시점 hidden state** 사이의 연관도를 (예: dot product로) 계산하고, 이를 softmax로 정규화한 가중치로 인코더 hidden state들을 가중합해 **그 시점에 맞는 컨텍스트 벡터를 새로 만든다.** 그래서 입력의 필요한 부분을 직접 참조할 수 있다.

---

## 2. 이 아이디어는 누가, 어떻게, 어떤 문제를 풀려고 만들었나

> 출처 표기: **[확인]** = 이번에 논문/글을 직접 열어 확인한 것, **[배경]** = 일반적으로 알려진 내용이지만 이번에 원문을 열어보지 않은 것.

### 2-1. 큰 그림: 딥러닝은 "문제 발견 → 부분 해결 → 새 문제"의 연쇄로 발전했다

수업에서 본 흐름도 사실 한 줄로 이어진다. 각 단계는 **앞 단계가 못 푸는 구체적인 문제**를 풀려는 시도였다.

| 단계 | 앞 단계의 한계(문제) | 해결 시도 |
|---|---|---|
| 단일 퍼셉트론 | XOR 같은 비선형 문제를 못 푼다 **[배경]** (Minsky & Papert, 1969) | 은닉층 + 비선형 활성화 + 역전파로 다층 퍼셉트론 |
| 다층 퍼셉트론(Dense) | 이미지를 펼치면 파라미터가 너무 많고 위치 정보가 사라진다 | CNN: 필터를 공유해 지역 패턴을 본다 |
| CNN | 입력 길이가 가변이고 순서가 중요한 데이터(문장, 음성)에 맞지 않다 | RNN: 이전 상태를 다음 시점으로 넘긴다 |
| RNN | 긴 시퀀스에서 기울기가 사라져 먼 과거를 기억하지 못한다 **[배경]** | LSTM (Hochreiter & Schmidhuber, 1997, *Neural Computation*) |
| LSTM 단독 | 입력과 출력 길이가 다른 문제(번역 등)를 못 다룬다 | 인코더-디코더 / Seq2Seq (2014) |
| Seq2Seq | 입력 전체를 고정 크기 벡터 하나에 담는 **병목** | **Attention (2014)** |
| Attention + RNN | RNN은 순서대로 계산해야 해서 병렬화가 어렵고 느리다 | Transformer (2017): RNN 없이 attention만 사용 |

→ "누가 갑자기 천재적으로 떠올렸다"기보다, **직전 단계의 실패 지점이 명확했고 그 지점을 겨냥해 고친 것**이다.

### 2-2. Attention이 풀려던 정확한 문제: 고정 길이 벡터의 병목

**Seq2Seq의 등장 (2014)** **[확인]**
- Cho 등, *Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation* (2014.6, [arXiv:1406.1078](https://arxiv.org/abs/1406.1078)): 한 RNN이 입력을 **고정 길이 벡터**로 만들고, 다른 RNN이 그 벡터에서 출력 시퀀스를 생성하는 구조를 제안했다.
- Sutskever, Vinyals, Le, *Sequence to Sequence Learning with Neural Networks* (2014.9, [arXiv:1409.3215](https://arxiv.org/abs/1409.3215)): 깊은 LSTM으로 같은 구조를 번역에 적용했다. 이 논문은 원문 문장을 **거꾸로 넣으면** 성능이 크게 좋아진다고 보고했고(짧은 의존 관계가 많이 생겨 최적화가 쉬워진다고 설명), "긴 문장에서도 어려움이 없었다"고 주장했다.

**병목이 드러남** **[확인]**
- Cho 등, *On the Properties of Neural Machine Translation: Encoder-Decoder Approaches* (2014.9, [arXiv:1409.1259](https://arxiv.org/abs/1409.1259)): 이 인코더-디코더 번역은 짧은 문장에서는 잘 되지만 **문장이 길어지고 모르는 단어가 늘수록 성능이 빠르게 나빠진다**고 보고했다.
- 즉 2014년 당시에도 "긴 문장에서 되는가"는 모델과 설정에 따라 결과가 갈렸다. 내가 앞에서 정리한 "길면 병목"은 **모든 Seq2Seq가 반드시 실패한다는 뜻이 아니라, 고정 벡터가 구조적으로 짊어진 약점**이라고 이해하는 게 정확하다.

### 2-3. 누가, 어떤 과정으로 만들었나

**주인공**: Dzmitry Bahdanau, Kyunghyun Cho, Yoshua Bengio — *Neural Machine Translation by Jointly Learning to Align and Translate* ([arXiv:1409.0473](https://arxiv.org/abs/1409.0473), v1 2014.9.1, ICLR 2015 구두 발표) **[확인]**
- 이 논문이 문제의 원인을 직접 짚는다: 논문은 고정 길이 벡터가 **병목(bottleneck)이라고 추측**한다고 쓰고, 번역하는 단어마다 **원문에서 관련 있는 부분을 부드럽게 검색(soft search)** 하도록 하는 방법을 제안했다. 영어→프랑스어 번역에서 당시 최고 수준의 구(phrase) 기반 시스템과 비슷한 성능을 냈다고 보고했다.

**발상이 나온 과정 (Bahdanau 본인의 회고를 전한 2차 자료)** **[확인: Turing Post 글, 원 인터뷰는 직접 보지 못함]**
- Bahdanau는 Bengio 연구실의 **인턴**으로 들어와 Cho와 기계 번역 프로젝트를 했다.
- 첫 아이디어는 입력과 출력 시퀀스에 **커서 두 개**를 두고 움직이는 방식이었다. Alex Graves의 RNN Transducer에서 영감을 받았다고 한다. 하지만 번역에 쓰기엔 비현실적이고 인턴 기간에 구현하기에 너무 복잡해서, 더 단순한 방식으로 바꿨다.
- 핵심 통찰은 **"디코더가 입력의 어디를 볼지 스스로 학습하게 하자"** 였다. 그는 중학교 영어 번역 연습 때 시선이 원문과 번역문 사이를 오가던 경험에서 영감을 받았다고 말한다.
- 구조의 원래 이름은 **RNNSearch**였고, **"attention"이라는 이름은 나중에 Bengio가 붙인 것**이라고 Bahdanau는 말한다. (이 부분은 Turing Post가 Karpathy와의 대화를 인용해 전하는 내용이라, 원 출처를 직접 확인한 것은 아니다.)

**미리 있던 재료들**
- Graves, *Generating Sequences With Recurrent Neural Networks* (2013, [arXiv:1308.0850](https://arxiv.org/abs/1308.0850)): LSTM으로 손글씨를 생성하고, 텍스트 조건을 주어 "글자를 쓰게" 하는 모델. 글자와 펜 궤적을 맞추는 정렬 아이디어가 선행 작업이다. **[확인: 논문 존재와 내용]** (이 논문이 attention의 직접 영감이라는 설은 d2l.ai 교재 등의 설명이다.)
- **시각 쪽 attention**: Larochelle & Hinton, *Learning to combine foveal glimpses with a third-order Boltzmann machine* (NIPS 2010, [논문 페이지](https://papers.nips.cc/paper/2010/hash/677e09724f0e2df9b6c000b75b5da10d-Abstract.html))와 Mnih 등, *Recurrent Models of Visual Attention* (2014.6, [arXiv:1406.6247](https://arxiv.org/abs/1406.6247)). 이미지의 일부만 골라 보는 아이디어다. **[확인]**
  - 차이점: Mnih의 방식은 어디를 볼지 고르는 과정이 미분 불가능해서 강화학습으로 학습한다. Bahdanau의 방식은 모든 위치에 **가중치를 나눠 주는(soft) 미분 가능한 방식**이라 일반 역전파로 학습할 수 있다. 이 "soft"함이 실용성을 크게 높였다.
- 인터뷰에서 Bengio는 번역에서 사람이 입력 단어 몇 개에 집중하는 점, 그리고 이미지 attention 선행 연구에서 영향을 받았다고 말한다고 한다 (Turing Post 전언).

### 2-4. 정립과 확산

| 연도 | 논문 | 기여 |
|---|---|---|
| 2014 | Bahdanau, Cho, Bengio | 번역에 attention 도입. 점수는 작은 신경망(`v·tanh(W[…])` 꼴, 이후 *additive* 혹은 *concat*이라 부름)으로 계산. 직전 디코더 상태 사용 |
| 2015 | Luong, Pham, Manning, *Effective Approaches to Attention-based NMT* (EMNLP 2015, [arXiv:1508.04025](https://arxiv.org/abs/1508.04025)) | 구조를 단순화. **현재** 디코더 상태 h_t로 점수 계산. 점수 함수 3종 비교: `dot`(hₜᵀh̄ₛ), `general`(hₜᵀWₐh̄ₛ), `concat`. global/local attention. Bahdanau는 concat 하나만 실험했다고 지적 **[확인: ar5iv 본문]** |
| 2017 | Vaswani 등, *Attention Is All You Need* ([arXiv:1706.03762](https://arxiv.org/abs/1706.03762), 2017.6.12) | RNN과 합성곱을 모두 빼고 **attention만으로** 구성한 Transformer. WMT 2014 영어→독일어 28.4 BLEU, 병렬화 가능 **[확인]** |

→ 수업에서 배운 "디코더 hidden state와 인코더 hidden state의 dot product"는 이 표에서 **Luong 방식(dot)** 과 Transformer 계열의 방식에 해당한다.

### 2-5. "족적을 남기지 못하고 사라진" 시도들도 있었나?

네, 많다. 다만 **어느 것이 "효과 없는 알고리즘"이었는지는 후대에 살아남은 것만 기억되는 생존자 편향** 때문에 잘 안 보인다. 이번에 확인한 범위에서 보이는 사례는 이렇다.

- **Bahdanau 본인의 첫 아이디어(커서 두 개)**: 너무 복잡해서 버리고 더 단순한 방식으로 바꿨다. 실패한 시도가 최종 아이디어로 이어진 사례다. **[확인: Turing Post 전언]**
- **hard attention(강화학습 기반 시각 attention, Mnih 2014)**: 미분이 안 되어 학습이 까다롭다. NLP에서는 soft attention이 주류가 됐다. **[확인: 논문 초록]**
- **Cho 등의 gated recursive convolutional network**: 1409.1259에서 RNN 인코더-디코더와 함께 비교된 구조로 문장의 문법 구조를 자동 학습한다고 소개됐지만, 이후 번역 모델의 표준은 되지 않았다. **[확인: 초록]**
- **Schmidhuber의 Fast Weight Programmers(1992)**: 개념상 attention과 비슷하다는 지적이 있다. 다만 2014년 연구에 영향을 줬다는 증거는 없고, 당시에는 널리 쓰이지 않았다. **[확인: Turing Post 전언]**
- **퍼셉트론 → XOR 한계**: 1969년 단층 퍼셉트론의 한계가 지적된 뒤 신경망 연구가 한동안 위축된 시기가 있었다. **[배경]**

### 2-6. 내가 확인한 것과 못 한 것

- 확인함: 위 논문들의 제목·저자·제출일·초록(arXiv 페이지), Luong 논문의 점수 함수(ar5iv 본문), Bahdanau 회고의 2차 자료(Turing Post).
- **확인 못 함**: Bahdanau의 회고 **원문 인터뷰**, 퍼셉트론·LSTM 관련 [배경] 항목의 원문, "Bengio가 attention이라는 이름을 붙였다"는 발언의 직접 출처. Turing Post는 이를 인용하는 2차 자료이고, 같은 글에서 Schmidhuber는 자신이 1992년 논문에서 "attention"이라는 말을 먼저 썼다고 주장하며 글쓴이는 그 주장을 인정하지 않는다. 이 용어 문제는 논란이 있는 영역이니 단정해서 말하지 않는 것이 안전하다.

## 3. 우리 실습과 연결해 보기 (예상, 실험으로 확인한 것은 아님)

- `5_숫자거꾸로`와 `6_영대소5_15글자비교`에서는 **입력 길이가 5 → 15로 늘어날수록** 컨텍스트 벡터 하나(128차원)에 담아야 할 정보가 많아져 정확도가 떨어졌다. 병목이 원인 중 하나일 수 있다. (다만 Embedding 유무 등 다른 요인도 함께 달랐으므로 단정은 어렵다.)
- 역순 문제에 attention을 붙이면, 디코더의 첫 출력은 입력의 **마지막** 위치를, 두 번째 출력은 **끝에서 두 번째** 위치를 주로 보도록 학습될 것으로 예상된다. 즉 attention 가중치를 그림(히트맵)으로 그리면 **반대 방향 대각선**이 나올 것이다. 실습해 볼 만한 좋은 예제다.

---

## 참고 자료 (이번에 열어서 확인한 것)
- Bahdanau, Cho, Bengio (2014/2015), *Neural Machine Translation by Jointly Learning to Align and Translate* — <https://arxiv.org/abs/1409.0473>
- Cho 등 (2014), *Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation* — <https://arxiv.org/abs/1406.1078>
- Cho 등 (2014), *On the Properties of Neural Machine Translation: Encoder-Decoder Approaches* — <https://arxiv.org/abs/1409.1259>
- Sutskever, Vinyals, Le (2014), *Sequence to Sequence Learning with Neural Networks* — <https://arxiv.org/abs/1409.3215>
- Graves (2013), *Generating Sequences With Recurrent Neural Networks* — <https://arxiv.org/abs/1308.0850>
- Mnih, Heess, Graves, Kavukcuoglu (2014), *Recurrent Models of Visual Attention* — <https://arxiv.org/abs/1406.6247>
- Larochelle & Hinton (2010), *Learning to combine foveal glimpses with a third-order Boltzmann machine* — <https://papers.nips.cc/paper/2010/hash/677e09724f0e2df9b6c000b75b5da10d-Abstract.html>
- Luong, Pham, Manning (2015), *Effective Approaches to Attention-based Neural Machine Translation* — <https://arxiv.org/abs/1508.04025> (본문 확인: <https://ar5iv.labs.arxiv.org/html/1508.04025>)
- Vaswani 등 (2017), *Attention Is All You Need* — <https://arxiv.org/abs/1706.03762>
- Turing Post, *Attention Mechanism: Who Invented It and Why It Matters* (2차 자료) — <https://www.turingpost.com/p/attention>
- Dive into Deep Learning, *The Bahdanau Attention Mechanism* — <https://d2l.ai/chapter_attention-mechanisms-and-transformers/bahdanau-attention.html>

## 직접 확인하지 못한 것
- Hochreiter & Schmidhuber (1997), *Long Short-Term Memory*, Neural Computation 9(8) — LSTM 원 논문 (본문 미확인)
- Minsky & Papert (1969), *Perceptrons* — 단일 퍼셉트론의 한계 (미확인)
- Bahdanau 본인의 회고 원문 (Turing Post의 인용으로만 확인)
