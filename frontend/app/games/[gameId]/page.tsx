import { Dashboard } from "@/components/Dashboard";
import { dateFromGameId, isGameTab, isIsoDate } from "@/lib/dashboard-route";

export default async function GamePage({ params, searchParams }: {
  params: Promise<{ gameId: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const [{ gameId }, query] = await Promise.all([params, searchParams]);
  const queryDate = typeof query.date === "string" && isIsoDate(query.date) ? query.date : "";
  const date = queryDate || dateFromGameId(gameId);
  const tab = isGameTab(query.tab) ? query.tab : "overview";

  return <Dashboard initialDate={date} initialGameId={gameId} initialTab={tab} />;
}
