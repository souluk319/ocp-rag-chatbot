// 채팅 본문 렌더링과 citation/코드블록 표시를 담당하는 프론트 helper다.
window.createChatRenderer = function createChatRenderer(deps) {
  const refs = deps.refs;
  const helpers = deps.helpers;

  function appendInlineMarkup(target, text, citationsByIndex = null) {
    const tokens = (text || "").split(/(`[^`]+`|\*\*[^*]+\*\*|\[\d+\])/g);
    for (let index = 0; index < tokens.length; index += 1) {
      let token = tokens[index];
      if (!token) continue;
      if (token.startsWith("`") && token.endsWith("`") && token.length >= 2) {
        const code = document.createElement("code");
        code.className = "inline-code";
        code.textContent = token.slice(1, -1);
        target.appendChild(code);
        continue;
      }
      if (token.startsWith("**") && token.endsWith("**") && token.length >= 4) {
        const strong = document.createElement("strong");
        strong.textContent = token.slice(2, -2);
        target.appendChild(strong);
        continue;
      }
      if (/^\[\d+\]$/.test(token)) {
        const index = token.slice(1, -1);
        const citation = citationsByIndex ? citationsByIndex.get(index) : null;
        if (citation) {
          const nextToken = String(tokens[index + 1] || "");
          const leadingPunctuation = nextToken.match(/^(\s*)([.,!?;:]+)/);
          if (leadingPunctuation) {
            if (target.lastChild?.nodeType === Node.TEXT_NODE) {
              target.lastChild.textContent = target.lastChild.textContent.replace(/\s+$/u, "");
            }
            target.appendChild(document.createTextNode(leadingPunctuation[2]));
            tokens[index + 1] = nextToken.slice(leadingPunctuation[0].length);
          }
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
          continue;
        }
      }
      target.appendChild(document.createTextNode(token));
    }
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

  function toggleCodeWrap(block, button) {
    const wrapped = block.classList.toggle("is-wrapped");
    button.textContent = wrapped ? "줄바꿈 해제" : "줄바꿈";
    button.setAttribute("aria-pressed", wrapped ? "true" : "false");
  }

  function createCodeBlock(code, language = "") {
    const block = document.createElement("section");
    block.className = "code-block";

    const header = document.createElement("div");
    header.className = "code-block-header";

    const lang = document.createElement("span");
    lang.className = "code-lang";
    lang.textContent = language || "text";

    const actions = document.createElement("div");
    actions.className = "code-actions";

    const copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "code-copy";
    copyButton.textContent = "복사";
    copyButton.addEventListener("click", () => {
      void copyCodeToClipboard(code, copyButton);
    });

    const wrapButton = document.createElement("button");
    wrapButton.type = "button";
    wrapButton.className = "code-copy";
    wrapButton.textContent = "줄바꿈";
    wrapButton.setAttribute("aria-pressed", "false");
    wrapButton.addEventListener("click", () => {
      toggleCodeWrap(block, wrapButton);
    });

    const pre = document.createElement("pre");
    const codeEl = document.createElement("code");
    codeEl.textContent = code;
    pre.appendChild(codeEl);

    actions.append(copyButton, wrapButton);
    header.append(lang, actions);
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
    let listStart = null;
    let inCode = false;
    let codeLines = [];
    let codeLanguage = "";
    let codeTarget = "fragment";

    function flushParagraph() {
      if (!paragraphLines.length) return;
      fragment.appendChild(createParagraph(paragraphLines.join("\n"), citationsByIndex));
      paragraphLines = [];
    }

    function flushList() {
      if (!listItems.length) return;
      const list = document.createElement(listType === "ol" ? "ol" : "ul");
      if (listType === "ol" && Number.isFinite(listStart) && listStart > 1) {
        list.setAttribute("start", String(listStart));
      }
      listItems.forEach((item) => {
        const li = document.createElement("li");
        if (item.text) {
          appendInlineMarkup(li, item.text || "", citationsByIndex);
        }
        item.codeBlocks.forEach((block) => {
          li.appendChild(createCodeBlock(block.code, block.language));
        });
        list.appendChild(li);
      });
      fragment.appendChild(list);
      listItems = [];
      listType = "";
      listStart = null;
    }

    function appendCodeBlockToActiveList(code, language = "text") {
      if (!listItems.length) return false;
      listItems[listItems.length - 1].codeBlocks.push({ code, language });
      return true;
    }

    function flushCode() {
      const renderedCode = codeLines.join("\n");
      if (!appendCodeBlockToActiveList(renderedCode, codeLanguage || "text")) {
        fragment.appendChild(createCodeBlock(renderedCode, codeLanguage));
      }
      codeLines = [];
      codeLanguage = "";
      codeTarget = "fragment";
    }

    function looksLikeShellCommand(line) {
      const trimmed = String(line || "").trim();
      return /^(?:\$\s+)?(?:oc|kubectl|helm|docker|podman|etcdctl|systemctl|journalctl|curl|grep|awk|sed|cat|ls|rm|mv|cp|chmod|chown)\b/.test(trimmed);
    }

    lines.forEach((line) => {
      const fence = line.match(/^```([\w.+-]*)\s*$/);
      if (fence) {
        if (inCode) {
          flushCode();
          inCode = false;
        } else {
          flushParagraph();
          if (listItems.length) {
            codeTarget = "list-item";
          } else {
            flushList();
            codeTarget = "fragment";
          }
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
      const orderedItem = trimmed.match(/^(\d+)\.\s+(.*)$/);
      if (unorderedItem || orderedItem) {
        flushParagraph();
        const nextListType = orderedItem ? "ol" : "ul";
        if (listItems.length && listType !== nextListType) {
          flushList();
        }
        listType = nextListType;
        if (orderedItem && !Number.isFinite(listStart)) {
          listStart = Number(orderedItem[1]);
        }
        listItems.push({
          text: unorderedItem ? unorderedItem[1] : orderedItem[2],
          codeBlocks: [],
        });
        return;
      }

      if (looksLikeShellCommand(trimmed)) {
        flushParagraph();
        if (!appendCodeBlockToActiveList(trimmed, "bash")) {
          flushList();
          fragment.appendChild(createCodeBlock(trimmed, "bash"));
        }
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

  function renumberOrderedSteps(text) {
    const lines = String(text || "").split("\n");
    let nextStep = 1;
    return lines
      .map((line) => {
        const match = line.match(/^(\s*)(\d+)\.\s+(.*)$/);
        if (!match || match[1].length > 0) {
          return line;
        }
        return `${match[1]}${nextStep++}. ${match[3]}`;
      })
      .join("\n");
  }

  function normalizeAssistantAnswer(text) {
    let normalized = (text || "").trim();
    normalized = normalized.replace(/^답변:\s*/u, "");
    normalized = normalized.replace(/\n{2,}추가 가이드:\s*/gu, "\n\n**추가 가이드**\n");
    normalized = normalized.replace(/\n{2,}추가 안내:\s*/gu, "\n\n**추가 안내**\n");
    return renumberOrderedSteps(normalized);
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
    renumberOrderedSteps,
    renderAssistantBody,
    renderMarkdownInto,
    renderMessageBody,
  };
};
