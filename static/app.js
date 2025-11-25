// CSRF helper (Django docs)
function getCookie(name) {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith(name + "="));
  return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : null;
}
const csrftoken = getCookie("csrftoken");

async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken || "",
    },
    body: JSON.stringify(data || {}),
  });
  return res.json();
}

// Add to cart (product detail)
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("#btnAddToCart");
  if (!btn) return;
  const productId = btn.dataset.productId;
  const qtyInput = document.getElementById("qty");
  const qty = Math.max(1, parseInt(qtyInput?.value || "1", 10));

  const data = await postJSON("/cart/add/", { product_id: productId, qty });
  if (data.ok) {
    // simple UX hint; swap for a toast later
    alert("Added to cart!");
  } else {
    alert(data.error || "Could not add to cart");
  }
});

// Cart page: quantity change
document.addEventListener("change", async (e) => {
  const input = e.target.closest(".js-qty");
  if (!input) return;
  const tr = input.closest("tr");
  const productId = tr?.dataset.productId;
  const qty = Math.max(1, parseInt(input.value || "1", 10));

  const data = await postJSON("/cart/update/", { product_id: productId, qty });
  if (!data.ok) return alert(data.error || "Update failed");
  // recompute line & subtotal by reloading page for simplicity
  location.reload();
});

// Cart page: remove item
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".js-remove");
  if (!btn) return;
  const tr = btn.closest("tr");
  const productId = tr?.dataset.productId;

  const data = await postJSON("/cart/remove/", { product_id: productId });
  if (!data.ok) return alert(data.error || "Remove failed");
  location.reload();
});
