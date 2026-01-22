/* jshint esversion: 11, browser: true */
/* globals window, document, fetch */

function getCookie(name) {
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(name + "="));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
}

const CSRF = getCookie("csrftoken");

// Django to inject URLs; fallback to paths.
const APP_URLS = (window.APP_URLS || {
  cartAdd: "/cart/add/",
  cartUpdate: "/cart/update/",
  cartRemove: "/cart/remove/",
});

/**
 * POST JSON helper
 * @param {string} url
 * @param {object} data
 * @returns {Promise<object>}
 */
async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": CSRF || "",
      "X-Requested-With": "XMLHttpRequest",
    },
    body: JSON.stringify(data || {}),
  });
  // If non-2xx, read JSON error or throw
  if (!res.ok) {
    let msg = "Request failed";
    try {
      const err = await res.json();
      msg = err && err.error ? err.error : msg;
    } catch (_) { /* ignore */ }
    throw new Error(msg);
  }
  return res.json();
}

// 1) Product detail: Add to cart
document.addEventListener("click", async (ev) => {
  const btn = ev.target.closest("#btnAddToCart");
  if (!btn) return;

  try {
    const productId = btn.dataset.productId;
    const qtyEl = document.getElementById("qty");
    const qty = Math.max(1, parseInt((qtyEl && qtyEl.value) || "1", 10));

    await postJSON(APP_URLS.cartAdd, { product_id: productId, qty });

    alert("Added to cart");
  } catch (e) {
    alert(e.message || "Could not add to cart");
  }
});

// 2) Cart page: change quantity
document.addEventListener("change", async (ev) => {
  const input = ev.target.closest(".js-qty");
  if (!input) return;

  const row = input.closest("tr");
  const productId = row ? row.dataset.productId : null;
  if (!productId) return;

  const qty = Math.max(1, parseInt(input.value || "1", 10));
  try {
    await postJSON(APP_URLS.cartUpdate, { product_id: productId, qty });

    window.location.reload();
  } catch (e) {
    alert(e.message || "Update failed");
  }
});

// 3) Cart page: remove line
document.addEventListener("click", async (ev) => {
  const btn = ev.target.closest(".js-remove");
  if (!btn) return;

  const row = btn.closest("tr");
  const productId = row ? row.dataset.productId : null;
  if (!productId) return;

  try {
    await postJSON(APP_URLS.cartRemove, { product_id: productId });
    window.location.reload();
  } catch (e) {
    alert(e.message || "Remove failed");
  }
});
