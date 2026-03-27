/**
 * Data loader — reads from /public/data/frontend_data.json
 * All functions are server-safe (called in Next.js page components).
 */

let _cache = null;

export async function loadAllData() {
  if (_cache) return _cache;
  const res = await fetch('/data/frontend_data.json');
  _cache = await res.json();
  return _cache;
}

export function filterByModel(data, modelName) {
  return data
    .filter((item) => item.model === modelName)
    .map((item) => ({ id: item.pk, ...item.fields }));
}

export async function getProducts() {
  const data = await loadAllData();
  return filterByModel(data, 'goods.listmodel');
}

export async function getRentals() {
  const data = await loadAllData();
  return filterByModel(data, 'rentals.rentalitem');
}

export async function getStorageUnits() {
  const data = await loadAllData();
  return filterByModel(data, 'storage.storageunit');
}

export async function getLockers() {
  const data = await loadAllData();
  return filterByModel(data, 'lockers.locker');
}

export async function getWarehouse() {
  const data = await loadAllData();
  return filterByModel(data, 'warehouse.listmodel');
}

export async function getCoupons() {
  const data = await loadAllData();
  return filterByModel(data, 'coupons.coupon');
}

export async function getOrders() {
  const data = await loadAllData();
  return filterByModel(data, 'orders.order');
}

export async function getSuppliers() {
  const data = await loadAllData();
  return filterByModel(data, 'supplier.listmodel');
}
