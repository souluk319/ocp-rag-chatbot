window.OCP_PLAY_STUDIO_CONFIG = {
  corePacks: [
    { version: "4.20", label: "4.20", activeState: "사용 중", inactiveState: "선택", default: true },
    { version: "4.18", label: "4.18", activeState: "사용 중", inactiveState: "선택" },
    { version: "4.16", label: "4.16", activeState: "사용 중", inactiveState: "선택" },
  ],
  emptyStateSamples: [
    {
      label: "Pod Pending 점검 순서",
      query: "Pod가 Pending 상태에서 오래 멈춰 있을 때 어떤 순서로 점검해야 해?",
    },
    {
      label: "CrashLoopBackOff 원인 추적",
      query: "CrashLoopBackOff가 반복될 때 원인 추적 순서를 알려줘",
    },
    {
      label: "oc login / CLI 사용법",
      query: "oc login 기본 사용법과 토큰 로그인 예시를 알려줘",
    },
    {
      label: "Pod lifecycle 개념",
      query: "Pod lifecycle 개념을 초보자 관점에서 설명해줘",
    },
    {
      label: "Deployment 복제본 조정",
      query: "실행 중인 Deployment의 복제본 개수를 3개에서 5개로 변경하려면 어떻게 해야 해?",
    },
    {
      label: "Route / Ingress 차이",
      query: "OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘",
    },
    {
      label: "ImagePullBackOff 대응",
      query: "ImagePullBackOff가 발생하면 어떤 순서로 원인을 확인해야 해?",
    },
    {
      label: "ConfigMap / Secret 사용",
      query: "ConfigMap과 Secret을 언제 어떻게 나눠 써야 하는지 알려줘",
    },
  ],
};
