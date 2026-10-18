/* Decode, reveal, copy.
   The phone is old and the counter is busy, so: no framework, no build step,
   no animation library. One earned motion — the decode — and nothing else. */
(function () {
  "use strict";

  /* ---------- the decode: strip becomes a name ---------- */

  const rows = Array.prototype.slice.call(document.querySelectorAll(".row"));

  function panelFor(row) {
    const id = row.getAttribute("aria-controls");
    return id ? document.getElementById(id) : null;
  }

  function rowLabel(row, open) {
    const code = (row.querySelector(".code") || {}).textContent || "";
    const amount = (row.querySelector(".amount") || {}).textContent || "";
    const who = row.querySelector(".who");
    const name = who && who.dataset.name;
    if (open && name) {
      return "Entry " + code.trim() + ", " + amount.trim() + " outstanding, " +
        name + ". Hide the name and the message.";
    }
    return "Entry " + code.trim() + ", " + amount.trim() +
      " outstanding. Show the name and the message.";
  }

  function setOpen(row, open) {
    const panel = panelFor(row);
    const who = row.querySelector(".who");
    if (panel) {
      panel.classList.toggle("open", open);
      // A collapsed panel is clipped, not hidden, so its words stay findable and
      // printable. Only its controls are inert while closed: `inert` removes a
      // whole subtree from the accessibility tree, and the lineage and message
      // must not leave it.
      const tools = panel.querySelector(".tools");
      if (tools) tools.inert = !open;
    }
    row.setAttribute("aria-expanded", open ? "true" : "false");
    row.setAttribute("aria-label", rowLabel(row, open));
    if (who && who.dataset.name) {
      who.textContent = open ? who.dataset.name : "";
      who.classList.toggle("decoded", open);
    }
  }

  rows.forEach(function (row) {
    // Settle the server-rendered state: the first row ships open, and every
    // label must name the customer once that row is decoded.
    setOpen(row, row.getAttribute("aria-expanded") === "true");
  });

  rows.forEach(function (row) {
    row.addEventListener("click", function () {
      setOpen(row, row.getAttribute("aria-expanded") !== "true");
    });
  });

  /* ---------- reveal every name at once (for when the shop is empty) ---------- */

  const reveal = document.getElementById("reveal");
  if (reveal) {
    reveal.addEventListener("click", function () {
      const on = reveal.getAttribute("aria-pressed") !== "true";
      reveal.setAttribute("aria-pressed", on ? "true" : "false");
      reveal.textContent = on ? "Conceal" : "Reveal";
      rows.forEach(function (row) {
        setOpen(row, on);
      });
    });
  }

  /* ---------- copy ---------- */

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(
        function () {
          return true;
        },
        function () {
          return legacyCopy(text);
        }
      );
    }
    return Promise.resolve(legacyCopy(text));
  }

  function legacyCopy(text) {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "readonly");
    area.style.position = "fixed";
    area.style.top = "-1000px";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    let ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (err) {
      ok = false;
    }
    area.remove();
    return ok;
  }

  function announce(text) {
    const status = document.getElementById("status");
    if (!status) return;
    status.textContent = "";
    window.setTimeout(function () {
      status.textContent = text;
    }, 50);
  }

  document.querySelectorAll("[data-copy]").forEach(function (button) {
    const original = button.innerHTML;
    button.addEventListener("click", function () {
      const source = document.getElementById(button.dataset.copy);
      if (!source) return;
      const text = source.textContent.trim();
      copyText(text).then(function (ok) {
        button.innerHTML = ok ? "Copied" : "Select the message and copy it";
        button.classList.toggle("copy-flash", ok);
        announce(ok ? "Message copied" : "Copy failed. Select the message and copy it.");
        window.setTimeout(function () {
          button.innerHTML = original;
          button.classList.remove("copy-flash");
        }, 1800);
      });
    });
  });
})();
