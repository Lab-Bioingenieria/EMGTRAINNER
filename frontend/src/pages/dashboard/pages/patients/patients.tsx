import { Button } from "../../../../components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../../components/ui/card"
import { Badge } from "../../../../components/ui/badge"
import { Input } from "../../../../components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "../../../../components/ui/avatar"
import { Search, Plus, MoreVertical, Activity, Calendar, TrendingUp } from "lucide-react"
import { Link } from "react-router-dom"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../../../../components/ui/dropdown-menu"

const patients = [
  {
    id: "P-001",
    name: "John Doe",
    age: 34,
    device: "ProHand v3",
    lastSession: "2 hours ago",
    totalSessions: 45,
    accuracy: 96,
    status: "active",
    avatar: "/avatars/01.png",
  },
  {
    id: "P-002",
    name: "Jane Smith",
    age: 28,
    device: "ProArm v2",
    lastSession: "1 day ago",
    totalSessions: 32,
    accuracy: 94,
    status: "active",
    avatar: "/avatars/02.png",
  },
  {
    id: "P-003",
    name: "Mike Johnson",
    age: 42,
    device: "ProHand v3",
    lastSession: "3 days ago",
    totalSessions: 67,
    accuracy: 98,
    status: "active",
    avatar: "/avatars/03.png",
  },
  {
    id: "P-004",
    name: "Sarah Williams",
    age: 31,
    device: "ProArm v2",
    lastSession: "5 days ago",
    totalSessions: 28,
    accuracy: 92,
    status: "inactive",
    avatar: "/avatars/04.png",
  },
]

export default function PatientsPage() {
  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Patients</h1>
          <p className="text-muted-foreground">Select a patient to access their dashboard and lab interface</p>
        </div>
        <Button className="gap-2">
          <Plus className="size-4" />
          Add Patient
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search patients..." className="pl-9" />
        </div>
        <Button variant="outline">Filter</Button>
      </div>

      {/* Patient Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {patients.map((patient) => (
          <Card key={patient.id} className="transition-colors hover:border-primary/50 cursor-pointer">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <Avatar className="size-12">
                    <AvatarImage src={patient.avatar || "/placeholder.svg"} alt={patient.name} />
                    <AvatarFallback>
                      {patient.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-base">{patient.name}</CardTitle>
                    <CardDescription>
                      {patient.id} • {patient.age} years
                    </CardDescription>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreVertical className="size-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem>View Details</DropdownMenuItem>
                    <DropdownMenuItem>Edit Profile</DropdownMenuItem>
                    <DropdownMenuItem>Export Data</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Device</span>
                <Badge variant="outline">{patient.device}</Badge>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Activity className="size-3" />
                    <span>Sessions</span>
                  </div>
                  <p className="text-lg font-semibold">{patient.totalSessions}</p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <TrendingUp className="size-3" />
                    <span>Accuracy</span>
                  </div>
                  <p className="text-lg font-semibold">{patient.accuracy}%</p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Calendar className="size-3" />
                    <span>Status</span>
                  </div>
                  <Badge variant={patient.status === "active" ? "default" : "secondary"} className="text-xs">
                    {patient.status}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center justify-between border-t border-border pt-4">
                <span className="text-xs text-muted-foreground">Last session: {patient.lastSession}</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" asChild>
                    <Link to={`/dashboard/patients/${patient.id}/dashboard`}>Dashboard</Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link to={`/dashboard/patients/${patient.id}/lab`}>Launch Lab</Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

