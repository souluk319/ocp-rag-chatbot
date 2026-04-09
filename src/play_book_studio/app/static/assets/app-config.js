window.OCP_PLAY_STUDIO_CONFIG = {
  corePacks: [
    { version: "4.20", label: "OpenShift 4.20", activeState: "사용 중", inactiveState: "선택", default: true },
    { version: "4.18", label: "OpenShift 4.18", activeState: "사용 중", inactiveState: "선택" },
    { version: "4.16", label: "OpenShift 4.16", activeState: "사용 중", inactiveState: "선택" },
  ],
  emptyStateSamples: [
    {
      label: "etcd 백업 절차",
      query: "etcd 백업은 어떻게 하나?",
    },
    {
      label: "노드 사용량 확인",
      query: "oc adm top nodes는 언제 써?",
    },
    {
      label: "Route / Ingress 차이",
      query: "Route와 Ingress 차이가 뭐야?",
    },
    {
      label: "namespace admin 권한",
      query: "특정 namespace에 admin 권한 주는 법 알려줘",
    },
    {
      label: "Terminating 프로젝트 정리",
      query: "프로젝트가 Terminating에서 안 지워질 때 어떻게 해?",
    },
    {
      label: "아키텍처 소개",
      query: "OpenShift 아키텍처를 처음 설명해줘",
    },
    {
      label: "Operator 기본 개념",
      query: "Operator가 뭐고 왜 필요한가?",
    },
  ],
};
