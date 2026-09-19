const scenarios = {
  proof: {
    filename: "affine_regression_policy.toetra",
    sourceUrl: "https://github.com/KintanaOne/Toetra/blob/main/demo/regression/affine_regression_policy.toetra#L9-L13",
    sourceLabel: "Open the public regression demo",
    raw: 'model := "affine_score.joblib"\ntarget := score\n\nmaximum_score := 7.0\n\n[BOUND]:\nforall x0\nwith domain(x0.a: [0.0, 3.0])\n=> target[x0] <= maximum_score using Z3',
    code: '<span class="tok-key">model</span> <span class="tok-op">:=</span> <span class="tok-str">"affine_score.joblib"</span>\n<span class="tok-key">target</span> <span class="tok-op">:=</span> score\n\n<span class="tok-id">maximum_score</span> <span class="tok-op">:=</span> <span class="tok-num">7.0</span>\n\n<span class="tok-sec">[BOUND]:</span>\n<span class="tok-key">forall</span> x0\n<span class="tok-key">with domain</span>(x0.a: [<span class="tok-num">0.0</span>, <span class="tok-num">3.0</span>])\n<span class="tok-op">=&gt;</span> target[x0] <span class="tok-op">&lt;=</span> maximum_score <span class="tok-key">using</span> Z3',
    status: "PROVED",
    statusClass: "status-proved",
    summary: "The universal property holds across the declared input domain.",
    details: [
      ["Property", "BOUND"],
      ["Backend", "Z3"],
      ["Model route", "LinearRegression"],
      ["Formal scope", "∀ x0.a ∈ [0, 3]"]
    ]
  },
  counterexample: {
    filename: "binary_classification_policy.toetra",
    sourceUrl: "https://github.com/KintanaOne/Toetra/blob/main/demo/classification/binary_classification_policy.toetra#L9-L12",
    sourceLabel: "Open the public classification demo",
    raw: 'model := "binary_decision.joblib"\ntarget := decision\n\n[LOGIC]:\nforall applicant\nwith domain(applicant.income: [-1.0, 1.0])\n=> target[applicant].label == "yes" using Z3',
    code: '<span class="tok-key">model</span> <span class="tok-op">:=</span> <span class="tok-str">"binary_decision.joblib"</span>\n<span class="tok-key">target</span> <span class="tok-op">:=</span> decision\n\n<span class="tok-sec">[LOGIC]:</span>\n<span class="tok-key">forall</span> applicant\n<span class="tok-key">with domain</span>(applicant.income: [<span class="tok-num">-1.0</span>, <span class="tok-num">1.0</span>])\n<span class="tok-op">=&gt;</span> target[applicant].label <span class="tok-op">==</span> <span class="tok-str">"yes"</span> <span class="tok-key">using</span> Z3',
    status: "COUNTEREXAMPLE",
    statusClass: "status-counterexample",
    summary: "A concrete assignment violates the requested universal label property.",
    details: [
      ["Property", "LOGIC"],
      ["Backend", "Z3"],
      ["Model route", "LogisticRegression"],
      ["Example input", "income = 0.0"],
      ["Concrete replay", "label = \"no\" · p(\"yes\") = 0.500"]
    ]
  },
  witness: {
    filename: "binary_classification_policy.toetra",
    sourceUrl: "https://github.com/KintanaOne/Toetra/blob/main/demo/classification/binary_classification_policy.toetra#L14-L17",
    sourceLabel: "Open the public classification demo",
    raw: 'model := "binary_decision.joblib"\ntarget := decision\n\n[LOGIC]:\nexists applicant\nwith domain(applicant.income: [3.0, 6.0])\n=> target[applicant].probability("yes") >= 0.80 using Z3',
    code: '<span class="tok-key">model</span> <span class="tok-op">:=</span> <span class="tok-str">"binary_decision.joblib"</span>\n<span class="tok-key">target</span> <span class="tok-op">:=</span> decision\n\n<span class="tok-sec">[LOGIC]:</span>\n<span class="tok-key">exists</span> applicant\n<span class="tok-key">with domain</span>(applicant.income: [<span class="tok-num">3.0</span>, <span class="tok-num">6.0</span>])\n<span class="tok-op">=&gt;</span> target[applicant].probability(<span class="tok-str">"yes"</span>) <span class="tok-op">&gt;=</span> <span class="tok-num">0.80</span> <span class="tok-key">using</span> Z3',
    status: "WITNESS",
    statusClass: "status-witness",
    summary: "A satisfying assignment exists in the declared formal scope.",
    details: [
      ["Property", "LOGIC"],
      ["Backend", "Z3"],
      ["Observable", "probability(\"yes\")"],
      ["Example input", "income = 3.0"],
      ["Concrete replay", "p(\"yes\") ≈ 0.930"]
    ]
  }
};

const codeNode = document.querySelector("[data-code]");
const filenameNode = document.querySelector("[data-filename]");
const statusNode = document.querySelector("[data-status]");
const summaryNode = document.querySelector("[data-summary]");
const detailsNode = document.querySelector("[data-details]");
const runButton = document.querySelector("[data-run]");
const runNote = document.querySelector("[data-run-note]");
const workbench = document.querySelector(".verification-workbench");
const stageItems = Array.from(document.querySelectorAll("[data-stages] li"));
const scenarioButtons = Array.from(document.querySelectorAll("[data-scenario]"));
const scenarioPanel = document.querySelector("[data-scenario-panel]");
const scenarioSource = document.querySelector("[data-scenario-source]");
const sourceLabel = document.querySelector("[data-source-label]");
const copyStatus = document.querySelector("[data-copy-status]");
let activeScenario = "proof";
let runToken = 0;

function announceCopy(message) {
  copyStatus.textContent = "";
  window.requestAnimationFrame(() => {
    copyStatus.textContent = message;
  });
}

function setScenario(name) {
  activeScenario = name;
  runToken += 1;
  const scenario = scenarios[name];
  codeNode.innerHTML = scenario.code;
  filenameNode.textContent = scenario.filename;
  scenarioSource.href = scenario.sourceUrl;
  sourceLabel.textContent = scenario.sourceLabel;
  renderEvidence(scenario);
  workbench.classList.remove("is-running");
  runButton.disabled = false;
  runButton.querySelector("span").textContent = "Play this example";
  runNote.textContent = "Ready · Z3 does not run in this browser";
  stageItems.forEach((item) => {
    item.classList.remove("is-active");
    item.classList.add("is-complete");
  });
  scenarioButtons.forEach((button) => {
    const isSelected = button.dataset.scenario === name;
    button.setAttribute("aria-selected", String(isSelected));
    button.tabIndex = isSelected ? 0 : -1;
    if (isSelected) scenarioPanel.setAttribute("aria-labelledby", button.id);
  });
}

function renderEvidence(scenario) {
  statusNode.className = "result-status " + scenario.statusClass;
  statusNode.innerHTML = "<i></i><span>" + scenario.status + "</span>";
  summaryNode.textContent = scenario.summary;
  detailsNode.innerHTML = scenario.details
    .map((item) => "<div><dt>" + item[0] + "</dt><dd>" + item[1] + "</dd></div>")
    .join("");
}

scenarioButtons.forEach((button, index) => {
  button.addEventListener("click", () => setScenario(button.dataset.scenario));
  button.addEventListener("keydown", (event) => {
    let nextIndex = null;
    if (event.key === "ArrowRight") nextIndex = (index + 1) % scenarioButtons.length;
    if (event.key === "ArrowLeft") nextIndex = (index - 1 + scenarioButtons.length) % scenarioButtons.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = scenarioButtons.length - 1;
    if (nextIndex === null) return;

    event.preventDefault();
    const nextButton = scenarioButtons[nextIndex];
    setScenario(nextButton.dataset.scenario);
    nextButton.focus();
  });
});

runButton.addEventListener("click", () => {
  const token = ++runToken;
  const scenario = scenarios[activeScenario];
  workbench.classList.remove("is-running");
  void workbench.offsetWidth;
  workbench.classList.add("is-running");
  runButton.disabled = true;
  runButton.querySelector("span").textContent = "Playing…";
  statusNode.className = "result-status status-running";
  statusNode.innerHTML = "<i></i><span>WALKTHROUGH</span>";
  summaryNode.textContent = "Following the precomputed path from specification to evidence…";
  runNote.textContent = "Animating the public 1.0.0rc4 verification path";
  stageItems.forEach((item) => item.classList.remove("is-active", "is-complete"));

  if (reduceMotion) {
    stageItems.forEach((item) => item.classList.add("is-complete"));
    renderEvidence(scenario);
    runButton.disabled = false;
    runButton.querySelector("span").textContent = "Play again";
    runNote.textContent = "Example complete · precomputed evidence restored";
    workbench.classList.remove("is-running");
    return;
  }

  stageItems.forEach((item, index) => {
    window.setTimeout(() => {
      if (token !== runToken) return;
      stageItems.forEach((other, otherIndex) => {
        other.classList.toggle("is-complete", otherIndex < index);
        other.classList.toggle("is-active", otherIndex === index);
      });
    }, index * 310);
  });

  window.setTimeout(() => {
    if (token !== runToken) return;
    stageItems.forEach((item) => {
      item.classList.remove("is-active");
      item.classList.add("is-complete");
    });
    renderEvidence(scenario);
    runButton.disabled = false;
    runButton.querySelector("span").textContent = "Play again";
    runNote.textContent = "Example complete · precomputed evidence restored";
    workbench.classList.remove("is-running");
  }, 1700);
});

document.querySelector("[data-copy-code]").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  try {
    await navigator.clipboard.writeText(scenarios[activeScenario].raw);
    button.setAttribute("aria-label", "Property copied");
    announceCopy("Toetra property copied to the clipboard.");
    window.setTimeout(() => button.setAttribute("aria-label", "Copy Toetra property"), 1500);
  } catch (_) {
    button.setAttribute("aria-label", "Copy unavailable");
    announceCopy("Clipboard access is unavailable.");
  }
});

document.querySelectorAll("[data-copy-target]").forEach((button) => {
  button.addEventListener("click", async () => {
    const target = document.getElementById(button.dataset.copyTarget);
    try {
      await navigator.clipboard.writeText(target.innerText.replace(/^\$ /gm, ""));
      const original = button.textContent;
      button.textContent = "Copied";
      announceCopy("Quickstart commands copied to the clipboard.");
      window.setTimeout(() => { button.textContent = original; }, 1500);
    } catch (_) {
      button.textContent = "Unavailable";
      announceCopy("Clipboard access is unavailable.");
    }
  });
});

const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");
const navLabel = document.querySelector("[data-nav-label]");
const mobileNav = window.matchMedia("(max-width: 820px)");

function setNavigation(open, returnFocus = false) {
  const isOpen = mobileNav.matches && open;
  navToggle.setAttribute("aria-expanded", String(isOpen));
  navLabel.textContent = isOpen ? "Close navigation" : "Open navigation";
  nav.classList.toggle("is-open", isOpen);
  nav.inert = mobileNav.matches && !isOpen;
  if (mobileNav.matches) nav.setAttribute("aria-hidden", String(!isOpen));
  else nav.removeAttribute("aria-hidden");
  document.body.style.overflow = isOpen ? "hidden" : "";
  if (returnFocus) navToggle.focus();
}

navToggle.addEventListener("click", () => {
  setNavigation(navToggle.getAttribute("aria-expanded") !== "true");
});

nav.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => setNavigation(false));
});

function closeNavigation() {
  setNavigation(false, true);
}

document.addEventListener("keydown", (event) => {
  const isOpen = navToggle.getAttribute("aria-expanded") === "true";
  if (event.key === "Escape" && isOpen) closeNavigation();
  if (event.key !== "Tab" || !isOpen) return;

  const focusable = [navToggle, ...nav.querySelectorAll("a")];
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
});

if (typeof mobileNav.addEventListener === "function") {
  mobileNav.addEventListener("change", () => setNavigation(false));
} else {
  mobileNav.addListener(() => setNavigation(false));
}

setNavigation(false);

const header = document.querySelector("[data-header]");
const progress = document.querySelector(".scroll-progress span");

function updateScrollState() {
  header.classList.toggle("is-scrolled", window.scrollY > 18);
  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  progress.style.width = (scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0) + "%";
}

window.addEventListener("scroll", updateScrollState, { passive: true });
updateScrollState();

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealItems = document.querySelectorAll(".reveal");

if (reduceMotion || !("IntersectionObserver" in window)) {
  revealItems.forEach((item) => item.classList.add("is-visible"));
} else {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealItems.forEach((item) => observer.observe(item));
}

const parallax = document.querySelector("[data-parallax]");
if (!reduceMotion && window.matchMedia("(pointer: fine)").matches) {
  window.addEventListener("pointermove", (event) => {
    const x = (event.clientX / window.innerWidth - 0.5) * 8;
    const y = (event.clientY / window.innerHeight - 0.5) * 8;
    parallax.style.transform = "translate3d(" + x + "px," + y + "px,0)";
  }, { passive: true });
}

document.documentElement.classList.add("enhanced");
setScenario("proof");
