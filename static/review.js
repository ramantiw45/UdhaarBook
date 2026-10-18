/* Editable review table. No framework, because the counter's machine is old
   and the shopkeeper is standing up. */
(function () {
  const tbody = document.querySelector("#rows-table tbody");

  /* Drawn, not typed: a five-point star, not a dingbat. */
  const REMOVE_ICON =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12"/><path d="M18 6L6 18"/></svg>';

  function rowTemplate(row) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td data-label="Customer"><input class="cell name" value="${escapeAttr(row.name || "")}" aria-label="Customer name" /></td>
      <td data-label="Amount"><input class="cell amount" type="number" step="0.01" min="0" value="${row.amount || 0}" aria-label="Amount in rupees" /></td>
      <td data-label="Direction">
        <select class="cell direction" aria-label="Direction">
          <option value="udhaar"${row.direction === "udhaar" ? " selected" : ""}>udhaar — given</option>
          <option value="payment"${row.direction === "payment" ? " selected" : ""}>jama — paid</option>
        </select>
      </td>
      <td data-label="For"><input class="cell note" value="${escapeAttr(row.note || "")}" aria-label="What it was for" /></td>
      <td data-label="Date"><input class="cell date" value="${escapeAttr(row.date || "")}" aria-label="Date as written" /></td>
      <td data-label="Remove"><button type="button" class="act small remove" aria-label="Remove this line">${REMOVE_ICON}</button></td>
    `;
    tr.querySelector(".remove").addEventListener("click", () => tr.remove());
    return tr;
  }

  function escapeAttr(value) {
    return String(value).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
  }

  function collect() {
    return [...tbody.querySelectorAll("tr")]
      .map((tr) => ({
        name: tr.querySelector(".name").value.trim(),
        amount: parseFloat(tr.querySelector(".amount").value || "0"),
        direction: tr.querySelector(".direction").value,
        note: tr.querySelector(".note").value.trim(),
        date: tr.querySelector(".date").value.trim(),
      }))
      .filter((r) => r.name && r.amount > 0);
  }

  (ROWS.length ? ROWS : [{}]).forEach((row) => tbody.appendChild(rowTemplate(row)));

  document.querySelector("#add-row").addEventListener("click", () => {
    tbody.appendChild(rowTemplate({ direction: "udhaar" }));
  });

  document.querySelector("#save").addEventListener("click", async () => {
    const status = document.querySelector("#save-status");
    const rows = collect();
    if (!rows.length) {
      status.textContent = "Nothing to save yet — every row needs a name and an amount.";
      return;
    }
    status.textContent = "Saving…";
    try {
      const resp = await fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scan_id: SCAN_ID, lane: LANE, rows }),
      });
      const data = await resp.json();
      status.textContent = `Saved ${data.saved} line(s). Opening the ledger…`;
      window.location.href = data.redirect || "/ledger";
    } catch (err) {
      status.textContent = "Could not save: " + err.message;
    }
  });
})();
