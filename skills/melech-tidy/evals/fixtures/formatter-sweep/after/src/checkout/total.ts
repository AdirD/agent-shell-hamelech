import { Cart, LineItem } from "./types";
import { roundCurrency } from "./money";

export function lineTotal(item: LineItem): number {
  return item.unitPrice * item.quantity;
}

export function subtotal(cart: Cart): number {
  return cart.items.reduce((sum, item) => sum + lineTotal(item), 0);
}

export function calculateTotal(cart: Cart): number {
  const discount = cart.discount?.amount ?? 0;
  return roundCurrency(subtotal(cart) - discount);
}
