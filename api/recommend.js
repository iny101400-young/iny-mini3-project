// Vercel 서버 함수: POST /api/recommend
// 브라우저는 조건(예산, Citation)만 보낸다. 후보 목록은 서버가 data/data.json에서 직접 다시 만든다.
// GEMINI_API_KEY는 서버 환경 변수에서만 읽으므로 브라우저로 전달되지 않는다.

// 비교 데이터 (Vercel이 이 파일을 함수와 함께 묶어 배포한다)
const items = require("../data/data.json");

// Google Gemini Interactions API 주소와 모델 (ai.google.dev 공식 문서 기준)
const GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions";
// gemini-3.5-flash-lite: 공식 문서의 안정(Stable) 모델, 새 프로젝트 권장 모델 중 하나
const MODEL = "gemini-3.5-flash-lite";
// AI에게 넘길 후보 최대 개수 (M12 명세)
const MAX_CANDIDATES = 5;

// data.json에 실제로 있는 citation 값 목록
const CITATION_VALUES = [...new Set(items.map((item) => item.citation))];

// AI에게 주는 규칙 (M12 명세 + M12 도전: 같은 입력이면 같은 기준)
const SYSTEM_INSTRUCTION = [
  "너는 PDF AI 도구 후보 표에서 1개를 고르는 도우미다.",
  "반드시 입력으로 받은 candidates 안에서만 1개를 고른다. name은 후보 표의 이름을 글자 그대로 쓴다.",
  "추천 이유는 정확히 2줄이다. 이유에는 후보 표의 price와 citation 값만 사용한다.",
  "이유에는 추천한 후보의 price를 $숫자 형태로, citation을 Yes 또는 No 그대로 적는다.",
  "price 외의 숫자(순위, 개수, 비율, 예산 등)는 이유에 쓰지 않는다.",
  "후보 표에 없는 기능, 성능, 인기, 품질, 사용 후기는 만들어 말하지 않는다.",
  "같은 조건과 같은 후보 목록이 들어오면 항상 같은 기준으로 같은 1개를 고른다.",
].join("\n");

// 예산 값을 확인하는 함수 (null이면 예산 조건 없음)
function readBudget(value) {
  // 비어 있으면 조건 없음
  if (value === null || value === undefined || value === "") return { ok: true, budget: null };
  // 숫자로 바꾼다
  const budget = Number(value);
  // 숫자가 아니거나 음수면 잘못된 입력
  if (!Number.isFinite(budget) || budget < 0) return { ok: false };
  // 올바른 예산을 돌려준다
  return { ok: true, budget };
}

// 조건에 맞는 후보를 price 낮은 순으로 최대 5개 고르는 함수 (index.html의 필터와 같은 규칙)
function pickCandidates(budget, citation) {
  return items
    // 예산은 이하(같은 값 포함), citation은 정확히 일치, 두 조건은 AND
    .filter((item) => (budget === null || item.price <= budget) && (citation === "" || item.citation === citation))
    // price 낮은 순, 같은 가격이면 이름 순으로 항상 같은 순서가 되게 한다
    .sort((a, b) => a.price - b.price || a.name.localeCompare(b.name))
    // 최대 5개만 남긴다
    .slice(0, MAX_CANDIDATES)
    // AI에게는 name · price · citation 세 값만 넘긴다
    .map(({ name, price, citation }) => ({ name, price, citation }));
}

// Gemini 응답에서 모델이 쓴 글자만 꺼내는 함수 (steps[].content[].text)
function readOutputText(body) {
  // 간단한 형태가 있으면 그대로 쓴다
  if (typeof body.output_text === "string") return body.output_text;
  // steps 중 model_output의 text 조각을 이어 붙인다
  return (body.steps || [])
    .filter((step) => step.type === "model_output")
    .flatMap((step) => step.content || [])
    .filter((part) => part.type === "text" && typeof part.text === "string")
    .map((part) => part.text)
    .join("");
}

// 추천 결과가 후보 표와 맞는지 확인하는 함수
function verify(result, candidates) {
  // 모양이 틀리면 실패
  if (!result || typeof result.name !== "string" || !Array.isArray(result.reasons) || result.reasons.length !== 2) return null;
  // 이유 2줄이 모두 글자인지 확인한다
  const reasons = result.reasons.map((line) => (typeof line === "string" ? line.trim() : ""));
  // 빈 줄이 있으면 실패
  if (reasons.some((line) => line === "")) return null;
  // 추천 이름이 전달한 후보 안에 글자 그대로 있어야 한다
  const picked = candidates.find((c) => c.name === result.name);
  // 없으면 실패
  if (!picked) return null;
  // 이유 2줄을 한 글자로 합친다
  const text = reasons.join(" ");
  // 이유에 나온 숫자를 모두 찾는다 (예: $9.99 → 9.99)
  const numbers = (text.match(/\d+(?:\.\d+)?/g) || []).map(Number);
  // 숫자는 모두 후보 표의 price 중 하나여야 한다
  const prices = candidates.map((c) => c.price);
  // 표에 없는 숫자가 있으면 실패
  if (!numbers.every((n) => prices.includes(n))) return null;
  // 추천한 후보의 price가 이유에 들어 있어야 한다
  if (!numbers.includes(picked.price)) return null;
  // 이유에 나온 Yes / No를 모두 찾는다
  const citations = text.match(/\b(Yes|No)\b/g) || [];
  // 추천한 후보의 citation 값이 이유에 들어 있어야 한다
  if (!citations.includes(picked.citation)) return null;
  // 표에 없는 citation 값이 있으면 실패
  if (!citations.every((c) => candidates.some((cand) => cand.citation === c))) return null;
  // 확인을 통과한 추천을 돌려준다
  return { name: picked.name, reasons };
}

// Vercel이 부르는 요청 처리 함수
module.exports = async function handler(req, res) {
  // POST만 받는다
  if (req.method !== "POST") {
    // 다른 방식이면 거절한다
    res.setHeader("Allow", "POST");
    return res.status(405).json({ status: "error" });
  }

  // 요청 본문 (Vercel이 JSON을 미리 풀어 준다)
  const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
  // 예산 조건을 확인한다
  const budgetCheck = readBudget(body.budget);
  // citation 조건 ("" 이면 조건 없음)
  const citation = typeof body.citation === "string" ? body.citation : "";
  // 잘못된 조건이면 거절한다
  if (!budgetCheck.ok || (citation !== "" && !CITATION_VALUES.includes(citation))) {
    return res.status(400).json({ status: "error" });
  }

  // 서버가 data.json으로 후보를 다시 만든다
  const candidates = pickCandidates(budgetCheck.budget, citation);
  // 후보가 0개면 Gemini를 부르지 않는다
  if (candidates.length === 0) return res.status(200).json({ status: "no_candidates" });

  // 서버 환경 변수에서만 키를 읽는다
  const apiKey = process.env.GEMINI_API_KEY;
  // 키가 없으면 다시 시도 안내로 처리한다
  if (!apiKey) return res.status(503).json({ status: "retry" });

  // AI에게 넘길 입력 (현재 조건 + 후보 최대 5개)
  const input = JSON.stringify({
    conditions: { budget_usd_max: budgetCheck.budget, citation: citation === "" ? null : citation },
    candidates,
  });

  // 응답 모양: 후보 이름 중 하나 + 이유 정확히 2줄
  const schema = {
    type: "object",
    properties: {
      name: { type: "string", enum: candidates.map((c) => c.name) },
      reasons: { type: "array", items: { type: "string" }, minItems: 2, maxItems: 2 },
    },
    required: ["name", "reasons"],
  };

  // Gemini 호출 결과를 담을 변수
  let apiResponse;
  try {
    // Interactions API를 부른다 (키는 헤더로만 보낸다)
    apiResponse = await fetch(GEMINI_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": apiKey },
      body: JSON.stringify({
        model: MODEL,
        system_instruction: SYSTEM_INSTRUCTION,
        input,
        // 같은 입력이면 같은 결과가 나오도록 무작위성을 낮춘다
        generation_config: { temperature: 0, seed: 7, thinking_level: "low", max_output_tokens: 512 },
        response_format: { type: "text", mime_type: "application/json", schema },
        // 요청·응답을 Google 쪽에 저장하지 않는다
        store: false,
      }),
      // 20초 안에 답이 없으면 멈춘다
      signal: AbortSignal.timeout(20000),
    });
  } catch (err) {
    // 네트워크 오류·시간 초과는 다시 시도 안내
    return res.status(503).json({ status: "retry" });
  }

  // 요청 한도 초과(429)나 다른 실패도 다시 시도 안내 (키나 응답 본문은 돌려주지 않는다)
  if (!apiResponse.ok) {
    console.error("Gemini 호출 실패: HTTP", apiResponse.status);
    return res.status(503).json({ status: "retry" });
  }

  // 모델이 쓴 JSON 글자를 풀어 본다
  let result;
  try {
    // 응답 본문을 읽는다
    const data = await apiResponse.json();
    // 모델 출력 글자를 JSON으로 푼다
    result = JSON.parse(readOutputText(data));
  } catch (err) {
    // 풀 수 없으면 확인 실패
    return res.status(200).json({ status: "unverified" });
  }

  // 후보 표와 맞는지 확인한다
  const verified = verify(result, candidates);
  // 맞지 않으면 결과를 보여 주지 않는다
  if (!verified) return res.status(200).json({ status: "unverified" });

  // 확인된 추천과 AI에게 넘긴 후보 이름을 돌려준다
  return res.status(200).json({ status: "ok", ...verified, candidates: candidates.map((c) => c.name), model: MODEL });
};
