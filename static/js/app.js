const form = document.querySelector("#rankingForm");
const fileInput = document.querySelector("#resumeFiles");
const fileSummary = document.querySelector("#fileSummary");
const rankButton = document.querySelector("#rankButton");
const resetButton = document.querySelector("#resetButton");
const emptyState = document.querySelector("#emptyState");
const resultsArea = document.querySelector("#resultsArea");
const bestName = document.querySelector("#bestName");
const bestScore = document.querySelector("#bestScore");
const resultsTable = document.querySelector("#resultsTable");
const downloadButton = document.querySelector("#downloadButton");
const toast = document.querySelector("#toast");
const candidateCount = document.querySelector("#candidateCount");
const topScore = document.querySelector("#topScore");
const strongCount = document.querySelector("#strongCount");
const skippedNotice = document.querySelector("#skippedNotice");

let latestResults = [];
let scoreChart;
let categoryChart;
let toastTimer;

const dropZone = document.querySelector(".drop-zone");
if (dropZone) {
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add("drag-over");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, () => {
      dropZone.classList.remove("drag-over");
    });
  });
}
fileInput.addEventListener("change", () => {
  const count = fileInput.files.length;
  fileSummary.textContent = summarizeFiles(fileInput.files);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoading(true);

  try {
    const formData = new FormData(form);
    const response = await fetch("/api/rank", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Unable to rank resumes.");
    }

    latestResults = payload.results;
    renderResults(payload);
  } catch (error) {
    showToast(error.message);
  } finally {
    setLoading(false);
  }
});

downloadButton.addEventListener("click", async () => {
  if (!latestResults.length) {
    showToast("Rank resumes before downloading CSV.");
    return;
  }

  try {
    const response = await fetch("/api/download", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ results: latestResults }),
    });

    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.error || "The CSV could not be created.");
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ranked_resumes.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (error) {
    showToast(error.message);
  }
});

resetButton.addEventListener("click", () => {
  form.reset();
  latestResults = [];
  fileSummary.textContent = "No files selected";
  emptyState.classList.remove("d-none");
  resultsArea.classList.add("d-none");
  candidateCount.textContent = "0";
  topScore.textContent = "0.00";
  strongCount.textContent = "0";

  if (scoreChart) {
    scoreChart.destroy();
  }
  if (categoryChart) {
    categoryChart.destroy();
  }
});

function renderResults(payload) {
  emptyState.classList.add("d-none");
  resultsArea.classList.remove("d-none");

  candidateCount.textContent = payload.results.length;
  topScore.textContent = payload.best_candidate.MatchScore.toFixed(2);
  strongCount.textContent = payload.category_counts.Strong || 0;

  bestName.textContent = payload.best_candidate.Name;
  bestScore.textContent = `${payload.best_candidate.MatchScore.toFixed(2)} match score`;

  if (payload.skipped && payload.skipped.length) {
    skippedNotice.textContent = `Skipped ${payload.skipped.length} unreadable or unsupported file(s): ${payload.skipped.join(", ")}`;
    skippedNotice.classList.remove("d-none");
  } else {
    skippedNotice.classList.add("d-none");
  }

  resultsTable.innerHTML = payload.results
    .map((result) => {
      const categoryClass = `category-${result.Category.toLowerCase()}`;
      return `
        <tr>
          <td class="fw-bold">${result.Rank}</td>
          <td>${escapeHtml(result.Name)}</td>
          <td><span class="score-pill">${result.MatchScore.toFixed(2)}</span></td>
          <td><span class="category-pill ${categoryClass}">${result.Category}</span></td>
        </tr>
      `;
    })
    .join("");

  renderScoreChart(payload.results);
  renderCategoryChart(payload.category_counts);
}

function renderScoreChart(results) {
  const context = document.querySelector("#scoreChart");

  if (scoreChart) {
    scoreChart.destroy();
  }

  scoreChart = new Chart(context, {
    type: "line",
    data: {
      labels: results.map((result) => result.Name),
      datasets: [
        {
          label: "Match score",
          data: results.map((result) => result.MatchScore),
          borderColor: "#2563eb",
          backgroundColor: "rgba(37, 99, 235, 0.12)",
          pointBackgroundColor: "#2563eb",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 4,
          tension: 0.3,
          fill: true,
        },
      ],
    },
    options: chartOptions("Candidate", "Match score", 100),
  });
}

function renderCategoryChart(categoryCounts) {
  const context = document.querySelector("#categoryChart");
  const labels = ["Strong", "Moderate", "Weak"];

  if (categoryChart) {
    categoryChart.destroy();
  }

  categoryChart = new Chart(context, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Resumes",
          data: labels.map((label) => categoryCounts[label] || 0),
          backgroundColor: ["#159447", "#b26a00", "#c2413b"],
          borderRadius: 6,
          maxBarThickness: 52,
        },
      ],
    },
    options: chartOptions("Category", "Resumes"),
  });
}

function chartOptions(xTitle, yTitle, suggestedMax) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        displayColors: false,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: xTitle,
        },
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 35,
          minRotation: 0,
          callback(value) {
            const label = this.getLabelForValue(value);
            return label.length > 18 ? `${label.slice(0, 18)}...` : label;
          },
        },
      },
      y: {
        beginAtZero: true,
        suggestedMax,
        title: {
          display: true,
          text: yTitle,
        },
      },
    },
  };
}

function setLoading(isLoading) {
  rankButton.disabled = isLoading;
  rankButton.innerHTML = isLoading
    ? '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span><span>Ranking</span>'
    : '<i class="bi bi-sort-down-alt me-2"></i><span>Rank Resumes</span>';
}

function showToast(message) {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.remove("d-none");
  toastTimer = window.setTimeout(() => toast.classList.add("d-none"), 3600);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return entities[character];
  });
}


function summarizeFiles(files) {
  const count = files.length;
  if (!count) {
    return "PDF or DOCX, multiple files supported";
  }

  const pdfCount = Array.from(files).filter((file) => file.name.toLowerCase().endsWith(".pdf")).length;
  const docxCount = Array.from(files).filter((file) => file.name.toLowerCase().endsWith(".docx")).length;
  const parts = [];

  if (pdfCount) {
    parts.push(`${pdfCount} PDF`);
  }
  if (docxCount) {
    parts.push(`${docxCount} DOCX`);
  }

  return `${count} file${count === 1 ? "" : "s"} selected${parts.length ? ` (${parts.join(", ")})` : ""}`;
}
