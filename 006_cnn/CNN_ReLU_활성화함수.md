# CNN Convolution Layer는 왜 활성화 함수로 ReLU를 쓸까?

CNN의 convolution layer에서 ReLU를 쓰는 이유는 크게 네 가지다.

## 1. 비선형성(non-linearity) 도입

Convolution 자체는 선형 연산(가중치 곱셈 + 합)이다. 만약 활성화 함수 없이 conv layer를 계속 쌓으면, 아무리 레이어를 깊게 쌓아도 결국 하나의 선형 변환과 수학적으로 동일해져 버린다(선형 함수의 합성은 여전히 선형). 그러면 복잡한 패턴(모서리 → 질감 → 형태 → 객체)을 계층적으로 학습하는 CNN의 의미가 없어진다. ReLU 같은 비선형 함수가 각 conv layer 사이에 들어가야 레이어를 쌓는 게 실제로 "더 복잡한 함수를 표현할 수 있게" 된다.

## 2. Gradient vanishing 문제 완화

이전에 많이 쓰이던 **sigmoid**나 **tanh**는 입력이 조금만 커지거나 작아져도 미분값(gradient)이 거의 0에 수렴한다(saturating). 레이어가 깊어질수록(CNN은 보통 수십~수백 layer) 이 작은 gradient들이 backpropagation 과정에서 계속 곱해지면서 **gradient vanishing**이 심해져 학습이 거의 멈춘다.

ReLU는 `f(x) = max(0, x)`라서, x>0 구간에서는 **기울기가 항상 1**이다. 그래서 깊은 네트워크에서도 gradient가 잘 전파된다 — 이게 2012년 AlexNet 이후 CNN이 훨씬 깊어질 수 있었던 핵심 이유 중 하나다.

## 3. 계산이 매우 가벼움

sigmoid/tanh는 지수함수(`exp`) 연산이 필요해서 느린데, ReLU는 `max(0, x)` 비교 연산 하나로 끝난다. CNN은 이미지 전체에 걸쳐 수백만 개의 뉴런에 활성화 함수를 적용해야 하므로, 이 연산 비용 차이가 실제 학습/추론 속도에 크게 영향을 준다.

## 4. Sparse activation (희소 활성화) 효과

입력이 음수면 그냥 0을 출력하므로, 한 레이어에서 실제로 "활성화되는"(0이 아닌) 뉴런 비율이 자연스럽게 줄어든다. 이는 특징(feature)들이 서로 덜 얽히게 만들어 표현력에 도움이 되고, 생물학적 뉴런의 동작 방식(자극이 임계치 이하면 발화 안 함)과도 어느 정도 유사하다고 설명된다.

## 참고: output layer는 다름

conv/hidden layer는 `relu`를 쓰지만, 마지막 출력층은 `sigmoid`(이진분류) 또는 `softmax`(다중분류)를 쓴다. 이건 출력을 확률(0~1)로 해석해야 하기 때문이고, hidden layer의 역할(특징 추출)과 output layer의 역할(확률 변환)이 다르기 때문이다.

## 참고: ReLU의 단점

ReLU는 입력이 음수면 gradient가 0이 돼서, 한번 완전히 죽어버린 뉴런(dying ReLU)은 더 이상 학습이 안 될 수 있다. 이를 완화하려고 `LeakyReLU`, `ELU` 같은 변형도 쓰이는데, 기본값으로는 ReLU가 "충분히 좋고 빠르다"는 이유로 가장 널리 쓰인다.
