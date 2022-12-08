# sitting-posture-recognition
## 산학프로젝트 챌린지 2022

### 참여자
컴퓨터공학과 석박통합과정 이문현, 컴퓨터공학과 석사과정 

### 프로젝트 목표

---

- 많은 현대인들이 잘못된 자세로 의자에 오래 앉아 근무하여 허리, 목 등 통증 호소
- 근무자들의 자세 관련 질병 예방을 위한 자세 판별 시스템
- 비디오와 센서 데이터를 수집하여 HAR (Human Activity / Action Recognition) 적용

![image](https://user-images.githubusercontent.com/80090973/204742497-df5f7958-18ea-4994-8db4-4bede9ca2689.png)

### Dataset

---

![image](https://user-images.githubusercontent.com/80090973/204742665-825e74f0-8219-4259-ab19-5421dd081f7a.png)

- 총 6개의 동작으로 구성되어 있습니다.
    - 앉아있기, 다리 떨기, 왼쪽/오른쪽으로 기울이기, 다리 꼬기, 구부정한 자세
- 비디오 수집 방법
    - 각 동작을 1분 동안 10초 간격으로 동작 반복 수행
- 센서 수집 방법
    - 다리, 머리에 모션 센서를 부착하여 Acceleration, Gyroscope 정보 수집
- 데이터 1차 전처리 (비디오)
    - 1분 1800 프레임을 5초 단위로 끊은 후 30 프레임만 사용
- 데이터 1차 전처리 (센서)
    - 1분 3000 프레임을 5초 단위로 끊은 후 30 프레임만 사용
- 데이터 2차 전처리 (비디오)
    - Random Crop, Resize, Color Distortion, Gaussian Noise
- 데이터 2차 전처리 (센서)
    - Small Noise


### Method

---
![image](https://user-images.githubusercontent.com/80090973/204742836-cba61804-93b5-45e9-b311-1d39ae42d025.png)


- 비디오 데이터와 센서 데이터를 활용한 Multi Modal HAR(Human Action Recognition) 방법
- 데이터 (비디오 & 센서) 학습을 위한 두개의 네트워크(Conv)와 하나의 분류기(Classifier) 사용
- Network
    - Video : ConvMixer
    - Sensor : Conv1D
    - Classifier : Conv1D
- 두 개의 네트워크 (Video & Sensor) 로부터 나온 마지막 feature map을 Concat하여 Classifier 학습
    - 비디오 프레임(2D 이미지)로부터 temporal, spatial 정보 추출
    - 센서 데이터를 비디오 프레임 만큼의 timestamp를 계산후 추출하여 feature map 추출
    - 추출된 비디오와 센서 각각의 feature vector를 Concat하여 prediction


### 프로젝트 결과

---

![image](https://user-images.githubusercontent.com/80090973/204743098-d4864c7c-d37c-4c93-ac15-91ff99bfd0fb.png)
![image](https://user-images.githubusercontent.com/80090973/204743158-2b769785-1edb-4b70-b01b-86bf948452a8.png)

- 비디오와 센서만을 사용했을 때 보다 함께 사용했을 때 테스트 정확도 향상
- But, 정확도가 안정적이지 못하고 튀는 현상
- 학습 데이터가 충분하다면 개선될 수 있을 것이라 예상
- 다양한 환경에서의 자세 예측 및 자세 교정 어플리케이션으로 확장 가능성
