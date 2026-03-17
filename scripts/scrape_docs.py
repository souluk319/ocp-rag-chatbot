"""OCP/Kubernetes 공식 문서 스크래핑 스크립트

수집 대상:
1. Red Hat OpenShift 4.17 공식 문서
2. Kubernetes 공식 문서 (Concepts)

사용법:
    python3 scripts/scrape_docs.py
    python3 scripts/scrape_docs.py --target ocp      # OCP만
    python3 scripts/scrape_docs.py --target k8s      # K8s만
    python3 scripts/scrape_docs.py --target all      # 전체 (기본값)
"""
import os
import sys
import re
import time
import argparse
import requests
from bs4 import BeautifulSoup

# 출력 디렉토리
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

# 요청 간 딜레이 (서버 부하 방지)
REQUEST_DELAY = 1.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ============================================================
# OCP 문서 URL 목록
# ============================================================
OCP_URLS = [
    # 아키텍처 & 개요
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/architecture/architecture",
        "filename": "ocp_architecture_overview.md",
        "category": "Architecture",
    },
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/architecture/control-plane",
        "filename": "ocp_control_plane.md",
        "category": "Architecture",
    },
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/architecture/architecture-rhcos",
        "filename": "ocp_rhcos.md",
        "category": "Architecture",
    },
    # 설치 & 업데이트
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/architecture/architecture-installation",
        "filename": "ocp_installation.md",
        "category": "Installation",
    },
    # 네트워킹
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/networking_overview/understanding-networking",
        "filename": "ocp_networking.md",
        "category": "Networking",
    },
    # 스토리지
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/storage/understanding-persistent-storage",
        "filename": "ocp_storage.md",
        "category": "Storage",
    },
    # 인증 & 보안
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/authentication_and_authorization/understanding-authentication",
        "filename": "ocp_authentication.md",
        "category": "Security",
    },
    # Operator
    {
        "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/operators/understanding-operators",
        "filename": "ocp_operators.md",
        "category": "Operators",
    },
]

# ============================================================
# Kubernetes 문서 URL 목록
# ============================================================
K8S_URLS = [
    {
        "url": "https://kubernetes.io/docs/concepts/overview/",
        "filename": "k8s_overview.md",
        "category": "Overview",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/overview/components/",
        "filename": "k8s_components.md",
        "category": "Overview",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/workloads/",
        "filename": "k8s_workloads.md",
        "category": "Workloads",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/workloads/pods/",
        "filename": "k8s_pods.md",
        "category": "Workloads",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/services-networking/",
        "filename": "k8s_networking.md",
        "category": "Networking",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/storage/",
        "filename": "k8s_storage.md",
        "category": "Storage",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/security/",
        "filename": "k8s_security.md",
        "category": "Security",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/configuration/",
        "filename": "k8s_configuration.md",
        "category": "Configuration",
    },
    {
        "url": "https://kubernetes.io/docs/concepts/cluster-administration/",
        "filename": "k8s_cluster_admin.md",
        "category": "Administration",
    },
]


def fetch_page(url: str) -> str | None:
    """URL에서 HTML 가져오기"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  [ERROR] {url}: {e}")
        return None


def extract_redhat_docs(html: str, url: str) -> str:
    """Red Hat 문서 HTML에서 본문 텍스트 추출 (마크다운 형식)"""
    soup = BeautifulSoup(html, "lxml")

    # Red Hat 문서의 본문 영역
    content = (
        soup.find("div", class_="rh-docs--content")
        or soup.find("main", id="main-content")
        or soup.find("article")
        or soup.find("div", class_="body")
        or soup.find("main")
    )
    if not content:
        content = soup.body or soup

    return _html_to_markdown(content, url)


def extract_k8s_docs(html: str, url: str) -> str:
    """Kubernetes 문서 HTML에서 본문 텍스트 추출 (마크다운 형식)"""
    soup = BeautifulSoup(html, "lxml")

    # K8s 문서의 본문 영역
    content = (
        soup.find("div", id="content")
        or soup.find("main", id="content")
        or soup.find("div", class_="td-content")
        or soup.find("main")
    )
    if not content:
        content = soup.body or soup

    return _html_to_markdown(content, url)


def _html_to_markdown(element, source_url: str) -> str:
    """HTML 요소를 마크다운 텍스트로 변환"""
    lines = []

    # 불필요한 요소 제거
    for tag in element.find_all(["nav", "footer", "header", "script", "style",
                                  "aside", "button", "form", "svg"]):
        tag.decompose()

    # 네비게이션/브레드크럼 제거
    for tag in element.find_all(class_=re.compile(
        r"(breadcrumb|sidebar|nav|menu|toc|pagination|footer|header|banner)", re.I
    )):
        tag.decompose()

    for child in element.descendants:
        if child.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(child.name[1])
            text = child.get_text(strip=True)
            if text:
                lines.append(f"\n{'#' * level} {text}\n")

        elif child.name == "p":
            text = child.get_text(strip=True)
            if text:
                lines.append(f"\n{text}\n")

        elif child.name == "li":
            text = child.get_text(strip=True)
            if text:
                lines.append(f"- {text}")

        elif child.name == "pre" or child.name == "code":
            # 코드 블록
            if child.parent and child.parent.name == "pre" and child.name == "code":
                continue  # pre > code 구조에서 code는 스킵
            text = child.get_text()
            if text.strip() and "\n" in text:
                lines.append(f"\n```\n{text.strip()}\n```\n")

        elif child.name == "table":
            _extract_table(child, lines)

        elif child.name == "dt":
            text = child.get_text(strip=True)
            if text:
                lines.append(f"\n**{text}**")

        elif child.name == "dd":
            text = child.get_text(strip=True)
            if text:
                lines.append(f"  {text}")

    # 출처 정보 추가
    result = "\n".join(lines)
    result = f"---\nSource: {source_url}\n---\n\n{result}"

    # 연속 빈 줄 정리
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def _extract_table(table, lines: list):
    """HTML 테이블을 마크다운 테이블로 변환"""
    rows = table.find_all("tr")
    if not rows:
        return

    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        cell_texts = [c.get_text(strip=True).replace("|", "\\|")[:100] for c in cells]
        if cell_texts:
            lines.append("| " + " | ".join(cell_texts) + " |")
            if i == 0:
                lines.append("| " + " | ".join(["---"] * len(cell_texts)) + " |")


def scrape_and_save(url_list: list, extractor_fn, label: str):
    """URL 목록을 스크래핑하고 파일로 저장"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    success = 0
    fail = 0

    print(f"\n{'='*60}")
    print(f"[{label}] 스크래핑 시작 ({len(url_list)}개 페이지)")
    print(f"{'='*60}")

    for i, item in enumerate(url_list, 1):
        url = item["url"]
        filename = item["filename"]
        category = item["category"]
        filepath = os.path.join(OUTPUT_DIR, filename)

        # 이미 존재하면 스킵
        if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
            print(f"  [{i}/{len(url_list)}] SKIP (exists): {filename}")
            success += 1
            continue

        print(f"  [{i}/{len(url_list)}] Fetching: {url[:80]}...")

        html = fetch_page(url)
        if not html:
            fail += 1
            continue

        # 본문 추출
        content = extractor_fn(html, url)
        if not content or len(content) < 50:
            print(f"    -> WARNING: 추출된 내용이 너무 짧습니다 ({len(content)}자)")
            fail += 1
            continue

        # 파일 헤더 추가
        header = f"# {category}\n\n"
        full_content = header + content

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        print(f"    -> OK: {len(full_content)}자 저장 ({filename})")
        success += 1
        time.sleep(REQUEST_DELAY)

    print(f"\n[{label}] 완료: 성공 {success}, 실패 {fail}")
    return success, fail


def main():
    parser = argparse.ArgumentParser(description="OCP/K8s 문서 스크래퍼")
    parser.add_argument("--target", choices=["ocp", "k8s", "all"], default="all",
                        help="스크래핑 대상 (기본: all)")
    args = parser.parse_args()

    total_success = 0
    total_fail = 0

    if args.target in ("ocp", "all"):
        s, f = scrape_and_save(OCP_URLS, extract_redhat_docs, "OCP Docs")
        total_success += s
        total_fail += f

    if args.target in ("k8s", "all"):
        s, f = scrape_and_save(K8S_URLS, extract_k8s_docs, "K8s Docs")
        total_success += s
        total_fail += f

    print(f"\n{'='*60}")
    print(f"전체 스크래핑 완료!")
    print(f"  성공: {total_success}")
    print(f"  실패: {total_fail}")
    print(f"  저장 경로: {OUTPUT_DIR}")
    print(f"\n다음 단계: python3 scripts/build_index.py")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
