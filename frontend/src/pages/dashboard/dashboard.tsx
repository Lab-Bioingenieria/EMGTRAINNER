"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card"
import { Badge } from "../../components/ui/badge"
import { Button } from "../../components/ui/button"
import { Activity, Users, Zap, Clock, TrendingUp, BarChart3, Play } from "lucide-react"
//import Link from "next/link"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../../components/ui/chart"
import { Area, AreaChart, Bar, BarChart, XAxis, YAxis } from "recharts"

const weeklyData = [
  { day: "Mon", sessions: 12, accuracy: 94 },
  { day: "Tue", sessions: 8, accuracy: 92 },
  { day: "Wed", sessions: 15, accuracy: 96 },
  { day: "Thu", sessions: 10, accuracy: 95 },
  { day: "Fri", sessions: 14, accuracy: 97 },
  { day: "Sat", sessions: 6, accuracy: 93 },
  { day: "Sun", sessions: 4, accuracy: 91 },
]

const recentSessions = [
  { id: "S-001", patient: "John Doe", duration: "45 min", accuracy: 96, status: "completed" },
  { id: "S-002", patient: "Jane Smith", duration: "32 min", accuracy: 94, status: "completed" },
  { id: "S-003", patient: "Mike Johnson", duration: "28 min", accuracy: 98, status: "processing" },
  { id: "S-004", patient: "Sarah Williams", duration: "51 min", accuracy: 92, status: "completed" },
]

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Overview of system activity and performance metrics</p>
        </div>
        <Button asChild>
          {/*<Link href="/lab">
            <Play className="mr-2 size-4" />
            Launch Lab
          </Link>*/}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <Activity className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,284</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-chart-1">+12%</span> from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Patients</CardTitle>
            <Users className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-chart-1">+3</span> new this week
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Accuracy</CardTitle>
            <Zap className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.7%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-chart-1">+2.1%</span> improvement
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Session Time</CardTitle>
            <Clock className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">38 min</div>
            <p className="text-xs text-muted-foreground">Optimal range: 30-45 min</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="size-5" />
              Weekly Sessions
            </CardTitle>
            <CardDescription>Number of sessions per day this week</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={{
                sessions: { label: "Sessions", color: "var(--primary)" },
              }}
              className="h-[200px] w-full"
            >
              <BarChart data={weeklyData}>
                <XAxis dataKey="day" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="sessions" fill="var(--primary)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="size-5" />
              Accuracy Trend
            </CardTitle>
            <CardDescription>Classification accuracy over the week</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={{
                accuracy: { label: "Accuracy %", color: "var(--chart-1)" },
              }}
              className="h-[200px] w-full"
            >
              <AreaChart data={weeklyData}>
                <XAxis dataKey="day" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} domain={[85, 100]} />
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
      </div>

      {/* Recent Sessions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Sessions</CardTitle>
          <CardDescription>Latest recorded sessions across all patients</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentSessions.map((session) => (
              <div key={session.id} className="flex items-center justify-between rounded-lg border border-border p-4">
                <div className="flex items-center gap-4">
                  <div className="flex size-10 items-center justify-center rounded-full bg-primary/10">
                    <Activity className="size-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">{session.patient}</p>
                    <p className="text-sm text-muted-foreground">
                      {session.id} • {session.duration}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-medium">{session.accuracy}%</p>
                    <p className="text-sm text-muted-foreground">Accuracy</p>
                  </div>
                  <Badge variant={session.status === "completed" ? "default" : "secondary"}>{session.status}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
