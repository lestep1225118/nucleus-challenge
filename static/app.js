const displayEl = document.getElementById("display");
const statusEl = document.getElementById("status");

let currentExpression = "";

function render() {
  displayEl.textContent = currentExpression || "0";
}

function setStatus(message, isError = false) {
  statusEl.textContent = message || "";
  statusEl.classList.toggle("error", isError);
}

function appendValue(value) {
  currentExpression += value;
  setStatus("");
  render();
}

function clearAll() {
  currentExpression = "";
  setStatus("");
  render();
}

function backspace() {
  currentExpression = currentExpression.slice(0, -1);
  render();
}

async function evaluate() {
  if (!currentExpression.trim()) {
    return;
  }
  setStatus("Calculating...");
  try {
    const res = await fetch("/api/calc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression: currentExpression })
    });

    const data = await res.json();
    if (!res.ok || data.error) {
      setStatus(data.error || "Error", true);
      return;
    }
    currentExpression = String(data.result);
    render();
    setStatus("OK");
  } catch (err) {
    setStatus("Network error", true);
  }
}

document.querySelectorAll(".btn").forEach((btn) => {
  const value = btn.getAttribute("data-value");
  const action = btn.getAttribute("data-action");

  if (value) {
    btn.addEventListener("click", () => appendValue(value));
  } else if (action === "clear") {
    btn.addEventListener("click", clearAll);
  } else if (action === "backspace") {
    btn.addEventListener("click", backspace);
  } else if (action === "equals") {
    btn.addEventListener("click", evaluate);
  }
});

document.addEventListener("keydown", (e) => {
  if (/[0-9+\-*/().]/.test(e.key)) {
    appendValue(e.key);
  } else if (e.key === "Enter") {
    e.preventDefault();
    evaluate();
  } else if (e.key === "Backspace") {
    backspace();
  } else if (e.key === "Escape") {
    clearAll();
  }
});

render();
