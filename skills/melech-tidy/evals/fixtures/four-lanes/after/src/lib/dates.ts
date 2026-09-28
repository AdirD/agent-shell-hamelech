export function formatDate(date: Date): string {
    return date.toISOString().slice(0, 10)
}

export function formatReportDate(date: Date): string {
    return `${formatDate(date)} (UTC)`
}
