/**
 * Cart store — uses localStorage so cart persists across pages.
 * Works entirely in browser, no backend needed.
 */

export function getCart() {
  if (typeof window === 'undefined') return [];
  try {
    return JSON.parse(localStorage.getItem('ms_cart') || '[]');
  } catch {
    return [];
  }
}

export function addToCart(item) {
  const cart = getCart();
  const existing = cart.find((c) => c.id === item.id && c.type === item.type);
  if (existing) {
    existing.qty = (existing.qty || 1) + 1;
  } else {
    cart.push({ ...item, qty: 1 });
  }
  localStorage.setItem('ms_cart', JSON.stringify(cart));
  window.dispatchEvent(new Event('cartUpdated'));
}

export function removeFromCart(id, type) {
  const cart = getCart().filter((c) => !(c.id === id && c.type === type));
  localStorage.setItem('ms_cart', JSON.stringify(cart));
  window.dispatchEvent(new Event('cartUpdated'));
}

export function updateQty(id, type, qty) {
  const cart = getCart().map((c) =>
    c.id === id && c.type === type ? { ...c, qty: Math.max(1, qty) } : c
  );
  localStorage.setItem('ms_cart', JSON.stringify(cart));
  window.dispatchEvent(new Event('cartUpdated'));
}

export function clearCart() {
  localStorage.removeItem('ms_cart');
  window.dispatchEvent(new Event('cartUpdated'));
}

export function getCartTotal(cart) {
  return cart.reduce((sum, item) => sum + (parseFloat(item.price) || 0) * (item.qty || 1), 0);
}

export function getCartCount(cart) {
  return cart.reduce((sum, item) => sum + (item.qty || 1), 0);
}
