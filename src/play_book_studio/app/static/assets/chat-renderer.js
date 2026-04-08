// 채팅 본문 렌더링과 citation/코드블록 표시를 담당하는 프론트 helper다.
window.createChatRenderer = function createChatRenderer(deps) {
  const refs = deps.refs;
  const helpers = deps.helpers;

  function appendInlineMarkup(target, text, citationsByIndex = null) {
    const tokens = (text || "").split(/(`[^`]+`|\*\*[^*]+\*\*|\[\d+\])/g);
    tokens.forEach((token) => {
      if (!token) return;
      if (token.startsWith("`") && token.endsWith("`") && token.length >= 2) {
        const code = document.createElement("code");
        code.className = "inline-code";
        code.textContent = token.slice(1, -1);
        target.appendChild(code);
        return;
      }
      if (token.startsWith("**") && token.endsWith("**") && token.length >= 4) {
        const strong = document.createElement("strong");
        strong.textContent = token.slice(2, -2);
        target.appendChild(strong);
        return;
      }
      if (/^\[\d+\]$/.test(token)) {
        const index = token.slice(1, -1);
        const citation = citationsByIndex ? citationsByIndex.get(index) : null;
        if (citation) {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = "inline-citation";
          chip.dataset.sourceKey = helpers.sourceKeyFor(citation);
          chip.setAttribute("aria-label", `참조 ${index} 열기`);
          chip.textContent = helpers.inlineCitationLabel(Number(index));
          chip.addEventListener("click", () => {
            void helpers.openSourcePanel(citation);
          });
          target.appendChild(chip);
          return;
        }
      }
      target.appendChild(document.createTextNode(token));
    });
  }

  function createParagraph(text, citationsByIndex = null) {
    const paragraph = document.createElement("p");
    const lines = (text || "").split("\n");
    lines.forEach((line, index) => {
      if (index > 0) paragraph.appendChild(document.createElement("br"));
      appendInlineMarkup(paragraph, line, citationsByIndex);
    });
    return paragraph;
  }

  async function copyCodeToClipboard(text, button) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const helper = document.createElement("textarea");
        helper.value = text;
        helper.setAttribute("readonly", "true");
        helper.style.position = "fixed";
        helper.style.opacity = "0";
        document.body.appendChild(helper);
        helper.select();
        document.execCommand("copy");
        document.body.removeChild(helper);
      }
      const original = button.textContent;
      button.textContent = "복사됨";
      button.classList.add("copied");
      window.setTimeout(() => {
        button.textContent = original;
        button.classList.remove("copied");
      }, 1400);
    } catch (error) {
      button.textContent = "실패";
      window.setTimeout(() => {
        button.textContent = "복사";
      }, 1400);
    }
  }

  function createCodeBlock(code, language = "") {
    const block = document.createElement("section");
    block.className = "code-block";

    const header = document.createElement("div");
    header.className = "code-block-header";

    const lang = document.createElement("span");
    lang.className = "code-lang";
    lang.textContent = language || "text";

    const copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "code-copy";
    copyButton.textContent = "복사";
    copyButton.addEventListener("click", () => {
      void copyCodeToClipboard(code, copyButton);
    });

    const pre = document.createElement("pre");
    const codeEl = document.createElement("code");
    codeEl.textContent = code;
    pre.appendChild(codeEl);

    header.append(lang, copyButton);
    block.append(header, pre);
    return block;
  }

  function renderMarkdownInto(element, text, citations = []) {
    element.innerHTML = "";
    const citationsByIndex = helpers.citationMapByIndex(citations);
    const fragment = document.createDocumentFragment();
    const lines = (text || "").replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
    let paragraphLines = [];
    let listItems = [];
    let listType = "";
    let inCode = false;
    let codeLines = [];
    let codeLanguage = "";

    function flushParagraph() {
      if (!paragraphLines.length) return;
      fragment.appendChild(createParagraph(paragraphLines.join("\n"), citationsByIndex));
      paragraphLines = [];
    }

    function flushList() {
      if (!listItems.length) return;
      const list = document.createElement(listType === "ol" ? "ol" : "ul");
      listItems.forEach((item) => {
        const li = document.createElement("li");
        appendInlineMarkup(li, item, citationsByIndex);
        list.appendChild(li);
      });
      fragment.appendChild(list);
      listItems = [];
      listType = "";
    }

    function flushCode() {
      fragment.appendChild(createCodeBlock(codeLines.join("\n"), codeLanguage));
      codeLines = [];
      codeLanguage = "";
    }

    lines.forEach((line) => {
      const fence = line.match(/^```([\w.+-]*)\s*$/);
      if (fence) {
        if (inCode) {
          flushCode();
          inCode = false;
        } else {
          flushParagraph();
          flushList();
          inCode = true;
          codeLanguage = fence[1] || "text";
        }
        return;
      }

      if (inCode) {
        codeLines.push(line);
        return;
      }

      const trimmed = line.trim();
      if (!trimmed) {
        flushParagraph();
        flushList();
        return;
      }

      const heading = trimmed.match(/^(#{1,3})\s+(.*)$/);
      if (heading) {
        flushParagraph();
        flushList();
        const headingEl = document.createElement(heading[1].length === 1 ? "h2" : "h3");
        appendInlineMarkup(headingEl, heading[2], citationsByIndex);
        fragment.appendChild(headingEl);
        return;
      }

      const unorderedItem = trimmed.match(/^[-*]\s+(.*)$/);
      const orderedItem = trimmed.match(/^\d+\.\s+(.*)$/);
      if (unorderedItem || orderedItem) {
        flushParagraph();
        const nextListType = orderedItem ? "ol" : "ul";
        if (listItems.length && listType !== nextListType) {
          flushList();
        }
        listType = nextListType;
        listItems.push((unorderedItem || orderedItem)[1]);
        return;
      }

      flushList();
      paragraphLines.push(trimmed);
    });

    flushParagraph();
    flushList();
    if (inCode) {
      flushCode();
    }

    if (!fragment.childNodes.length) {
      fragment.appendChild(createParagraph(text || "", citationsByIndex));
    }

    element.appendChild(fragment);
    refs.messagesEl.scrollTop = refs.messagesEl.scrollHeight;
  }

  function normalizeAssistantAnswer(text) {
    let normalized = (text || "").trim();
    normalized = normalized.replace(/^답변:\s*/u, "");
    normalized = normalized.replace(/\n{2,}추가 가이드:\s*/gu, "\n\n**추가 가이드**\n");
    normalized = normalized.replace(/\n{2,}추가 안내:\s*/gu, "\n\n**추가 안내**\n");
    return normalized;
  }

  function renderAssistantBody(element, text, citations = []) {
    element.innerHTML = "";

    const head = document.createElement("div");
    head.className = "assistant-head";

    const label = document.createElement("span");
    label.className = "assistant-label";
    label.textContent = "Answer";
    head.appendChild(label);

    const copy = document.createElement("div");
    copy.className = "assistant-copy";
    renderMarkdownInto(copy, normalizeAssistantAnswer(text), citations);

    const firstParagraph = copy.querySelector("p");
    if (firstParagraph) {
      firstParagraph.classList.add("assistant-lead");
    }

    element.append(head, copy);
  }

  function renderMessageBody(role, element, text, citations = []) {
    if (role === "assistant") {
      renderAssistantBody(element, text, citations);
      return;
    }
    element.textContent = text;
  }

  return {
    normalizeAssistantAnswer,
    renderAssistantBody,
    renderMarkdownInto,
    renderMessageBody,
  };
};
