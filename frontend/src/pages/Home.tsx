import {Link} from 'react-router-dom'
import {Button} from '../components/ui/button'
import {Card, CardDescription, CardHeader, CardTitle} from '../components/ui/card'
import { Activity, BarChart3, Cpu, Users, Zap } from "lucide-react"

function Home() {

    return (
        <div className="min-h-screen bg-background">
        {/* Hero Section */}
        <section className="relative overflow-hidden border-b border-border">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
            <div className="container relative mx-auto px-4 py-24">
            <div className="mx-auto max-w-3xl text-center">
                <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2 text-sm text-primary">
                <Cpu className="size-4" />
                <span>Advanced Prosthetic Control System</span>
                </div>
                <h1 className="mb-6 text-balance text-5xl font-bold tracking-tight lg:text-6xl">EMGControl</h1>
                <p className="mb-8 text-pretty text-lg text-muted-foreground leading-relaxed">
                Real-time monitoring, AI-powered control, and comprehensive analytics for prosthetic devices. Empowering
                researchers and clinicians with cutting-edge technology.
                </p>
                <div className="flex flex-wrap items-center justify-center gap-4">
                <Button asChild size="lg" className="gap-2">
                    <Link to='/dashboard'>Dashboard</Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="gap-2 bg-transparent">
                    <Link to='/lab'>Lab</Link>
                </Button>
                </div>
            </div>
            </div>
        </section>

        {/* Features Section */}
        <section className="container mx-auto px-4 py-20">
            <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold">System Capabilities</h2>
            <p className="text-muted-foreground">Comprehensive tools for prosthetic research and clinical applications</p>
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card className="border-border/50 transition-colors hover:border-primary/50">
                <CardHeader>
                <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-primary/10">
                    <Activity className="size-6 text-primary" />
                </div>
                <CardTitle>Real-Time Monitoring</CardTitle>
                <CardDescription>
                    Live EMG signal visualization and prosthetic movement tracking with sub-millisecond latency
                </CardDescription>
                </CardHeader>
            </Card>

            <Card className="border-border/50 transition-colors hover:border-primary/50">
                <CardHeader>
                <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-accent/10">
                    <Cpu className="size-6 text-accent" />
                </div>
                <CardTitle>AI-Powered Control</CardTitle>
                <CardDescription>
                    Machine learning models for accurate gesture recognition and adaptive motor control
                </CardDescription>
                </CardHeader>
            </Card>

            <Card className="border-border/50 transition-colors hover:border-primary/50">
                <CardHeader>
                <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-chart-3/10">
                    <BarChart3 className="size-6 text-chart-3" />
                </div>
                <CardTitle>Advanced Analytics</CardTitle>
                <CardDescription>
                    Comprehensive metrics including fatigue analysis, ROM calculations, and precision tracking
                </CardDescription>
                </CardHeader>
            </Card>

            <Card className="border-border/50 transition-colors hover:border-primary/50">
                <CardHeader>
                <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-chart-4/10">
                    <Zap className="size-6 text-chart-4" />
                </div>
                <CardTitle>3D Visualization</CardTitle>
                <CardDescription>
                    Interactive 3D models showing real-time prosthetic movements and joint angles
                </CardDescription>
                </CardHeader>
            </Card>

            <Card className="border-border/50 transition-colors hover:border-primary/50">
                <CardHeader>
                <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-chart-5/10">
                    <Activity className="size-6 text-chart-5" />
                </div>
                <CardTitle>Session Management</CardTitle>
                <CardDescription>
                    Record, replay, and analyze sessions with automatic metric calculation and CSV export
                </CardDescription>
                </CardHeader>
            </Card>

            <Card className="border-border/50 transition-colors hover:border-primary/50">
                <CardHeader>
                <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-primary/10">
                    <Users className="size-6 text-primary" />
                </div>
                <CardTitle>Patient Management</CardTitle>
                <CardDescription>
                    Comprehensive patient profiles with session history, progress tracking, and clinical notes
                </CardDescription>
                </CardHeader>
            </Card>
            </div>
        </section>
        </div>
      )
}

export default Home