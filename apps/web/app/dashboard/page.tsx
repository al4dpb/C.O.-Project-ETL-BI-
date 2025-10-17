import { getBIData } from "@/lib/bi";
import Link from "next/link";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function DashboardPage() {
  // Fetch live data from BI API
  const [propertyData, revenueData] = await Promise.all([
    getBIData.propertyOverview().catch(() => ({ data: [], row_count: 0, columns: [], query_name: "" })),
    getBIData.revenueTrends().catch(() => ({ data: [], row_count: 0, columns: [], query_name: "" })),
  ]);

  // Calculate summary metrics
  const totalSuites = propertyData.data.reduce((sum, b) => sum + b.total_suites, 0);
  const occupiedSuites = propertyData.data.reduce((sum, b) => sum + b.occupied_suites, 0);
  const totalRevenue = propertyData.data.reduce((sum, b) => sum + b.monthly_revenue, 0);
  const avgOccupancy = totalSuites > 0 ? (occupiedSuites / totalSuites) * 100 : 0;

  // Latest revenue trend
  const latestTrend = revenueData.data[revenueData.data.length - 1];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link
          href="/dashboard/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Upload Data
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card
          title="Total Suites"
          value={totalSuites.toString()}
          subtitle={`${occupiedSuites} occupied`}
          icon="🏢"
        />
        <Card
          title="Occupancy Rate"
          value={`${avgOccupancy.toFixed(1)}%`}
          subtitle={`Across ${propertyData.data.length} buildings`}
          icon="📊"
        />
        <Card
          title="Monthly Revenue"
          value={`$${(totalRevenue / 1000).toFixed(1)}k`}
          subtitle="Total across portfolio"
          icon="💰"
        />
        <Card
          title="Avg Rent PSF"
          value={latestTrend?.avg_rent_psf ? `$${latestTrend.avg_rent_psf.toFixed(2)}` : "N/A"}
          subtitle="Latest month"
          icon="📈"
        />
      </div>

      {/* Property Overview Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold mb-4">Property Overview</h2>
        {propertyData.data.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Building</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Suites</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Occupied</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Occupancy</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total SF</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {propertyData.data.map((building, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{building.building_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{building.total_suites}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{building.occupied_suites}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{building.occupancy_rate.toFixed(1)}%</td>
                    <td className="px-4 py-3 text-sm text-gray-600">${building.monthly_revenue.toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{building.total_sqft.toLocaleString()} SF</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No property data available" />
        )}
      </div>

      {/* Revenue Trends */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-bold mb-4">Revenue Trends</h2>
        {revenueData.data.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Occupancy</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Rent PSF</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {revenueData.data.slice(-12).map((month, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{month.month}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">${month.total_revenue.toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{month.occupancy_rate.toFixed(1)}%</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {month.avg_rent_psf ? `$${month.avg_rent_psf.toFixed(2)}` : "N/A"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState message="No revenue data available" />
        )}
      </div>
    </div>
  );
}

function Card({ title, value, subtitle, icon }: { title: string; value: string; subtitle: string; icon: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
      <p className="text-xs text-gray-500">{subtitle}</p>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-gray-500">
      <svg className="w-16 h-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p className="text-sm">{message}</p>
      <Link href="/dashboard/upload" className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium">
        Upload data to get started →
      </Link>
    </div>
  );
}
