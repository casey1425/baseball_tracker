import { Dashboard } from "@/components/Dashboard";
import { isGameTab, isIsoDate } from "@/lib/dashboard-route";

export default async function Home({ searchParams }: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = await searchParams;
  const date = typeof query.date === "string" && isIsoDate(query.date) ? query.date : "";
  const tab = isGameTab(query.tab) ? query.tab : "overview";
  return <Dashboard initialDate={date} initialTab={tab} />;
}
