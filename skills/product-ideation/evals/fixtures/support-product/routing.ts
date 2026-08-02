export type Ticket = {
  subject: string;
  body: string;
  customerPlan?: "free" | "pro" | "enterprise";
};

export type RoutingRule = {
  keywords: string[];
  teamId: string;
  priority?: "low" | "normal" | "high";
};

export function routeTicket(ticket: Ticket, rules: RoutingRule[]) {
  const text = `${ticket.subject} ${ticket.body}`.toLowerCase();

  for (const rule of rules) {
    if (rule.keywords.some((keyword) => text.includes(keyword.toLowerCase()))) {
      return { teamId: rule.teamId, priority: rule.priority ?? "normal" };
    }
  }

  return null;
}
