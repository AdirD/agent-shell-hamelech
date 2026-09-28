export type LineItem = {
    unitPrice: number
    quantity: number
}

export type Cart = {
    items: LineItem[]
    discount?: { amount: number }
}
