import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../../components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../../../components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../../components/ui/select"
import { TrendingUp, TrendingDown, Activity, Target, Zap, Clock } from "lucide-react"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../../../../components/ui/chart"
import { Area, AreaChart, Bar, BarChart, Line, LineChart, XAxis, YAxis } from "recharts"

const monthlyData = [
  { month: "Jan", sessions: 45, accuracy: 89, fatigue: 34 },
  { month: "Feb", sessions: 52, accuracy: 91, fatigue: 31 },
  { month: "Mar", sessions: 48, accuracy: 90, fatigue: 33 },
  { month: "Apr", sessions: 61, accuracy: 93, fatigue: 28 },
  { month: "May", sessions: 55, accuracy: 92, fatigue: 30 },
  { month: "Jun", sessions: 67, accuracy: 95, fatigue: 25 },
]

const patientComparison = [
  { name: "John D.", accuracy: 96, sessions: 45 },
  { name: "Jane S.", accuracy: 94, sessions: 32 },
  { name: "Mike J.", accuracy: 98, sessions: 67 },
  { name: "Sarah W.", accuracy: 92, sessions: 28 },
  { name: "Tom B.", accuracy: 95, sessions: 41 },
]

export default function AnalyticsPage() {
  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">Comprehensive analysis of system performance and patient progress</p>
        </div>
        <Select defaultValue="6months">
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7days">Last 7 days</SelectItem>
            <SelectItem value="30days">Last 30 days</SelectItem>
            <SelectItem value="6months">Last 6 months</SelectItem>
            <SelectItem value="1year">Last year</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <Activity className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">328</div>
            <div className="flex items-center text-xs text-chart-1">
              <TrendingUp className="mr-1 size-3" />
              +18% from last period
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Accuracy</CardTitle>
            <Target className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <div className="flex items-center text-xs text-chart-1">
              <TrendingUp className="mr-1 size-3" />
              +3.1% improvement
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Fatigue</CardTitle>
            <Zap className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">28.5%</div>
            <div className="flex items-center text-xs text-chart-1">
              <TrendingDown className="mr-1 size-3" />
              -12% (improved)
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Time</CardTitle>
            <Clock className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">142h</div>
            <div className="flex items-center text-xs text-muted-foreground">Avg. 26 min/session</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="accuracy">Accuracy</TabsTrigger>
          <TabsTrigger value="fatigue">Fatigue</TabsTrigger>
          <TabsTrigger value="comparison">Patient Comparison</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Sessions Over Time</CardTitle>
                <CardDescription>Monthly session count trend</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    sessions: { label: "Sessions", color: "var(--primary)" },
                  }}
                  className="h-[300px] w-full"
                >
                  <BarChart data={monthlyData}>
                    <XAxis dataKey="month" tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="sessions" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
                <CardDescription>Accuracy and fatigue trends</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    accuracy: { label: "Accuracy %", color: "var(--chart-1)" },
                    fatigue: { label: "Fatigue %", color: "var(--chart-2)" },
                  }}
                  className="h-[300px] w-full"
                >
                  <LineChart data={monthlyData}>
                    <XAxis dataKey="month" tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Line type="monotone" dataKey="accuracy" stroke="var(--chart-1)" strokeWidth={2} />
                    <Line type="monotone" dataKey="fatigue" stroke="var(--chart-2)" strokeWidth={2} />
                  </LineChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="accuracy">
          <Card>
            <CardHeader>
              <CardTitle>Accuracy Trend</CardTitle>
              <CardDescription>Classification accuracy over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  accuracy: { label: "Accuracy %", color: "var(--chart-1)" },
                }}
                className="h-[400px] w-full"
              >
                <AreaChart data={monthlyData}>
                  <XAxis dataKey="month" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} domain={[80, 100]} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Area
                    type="monotone"
                    dataKey="accuracy"
                    stroke="var(--chart-1)"
                    fill="var(--chart-1)"
                    fillOpacity={0.2}
                  />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fatigue">
          <Card>
            <CardHeader>
              <CardTitle>Fatigue Analysis</CardTitle>
              <CardDescription>Muscle fatigue levels over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  fatigue: { label: "Fatigue %", color: "var(--chart-2)" },
                }}
                className="h-[400px] w-full"
              >
                <AreaChart data={monthlyData}>
                  <XAxis dataKey="month" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} domain={[0, 50]} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Area
                    type="monotone"
                    dataKey="fatigue"
                    stroke="var(--chart-2)"
                    fill="var(--chart-2)"
                    fillOpacity={0.2}
                  />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comparison">
          <Card>
            <CardHeader>
              <CardTitle>Patient Comparison</CardTitle>
              <CardDescription>Accuracy comparison across patients</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  accuracy: { label: "Accuracy %", color: "var(--primary)" },
                }}
                className="h-[400px] w-full"
              >
                <BarChart data={patientComparison} layout="vertical">
                  <XAxis type="number" domain={[80, 100]} tickLine={false} axisLine={false} />
                  <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} width={80} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="accuracy" fill="var(--primary)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

