document.querySelectorAll(".copy").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const box = document.getElementById(btn.dataset.target);
    if (!box) return;
    try {
      await navigator.clipboard.writeText(box.value);
      btn.textContent = "Copied";
    } catch {
      box.select();
      document.execCommand("copy");
      btn.textContent = "Copied";
    }
    setTimeout(() => (btn.textContent = "Copy"), 1500);
  });
});
