import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../components/ui/card"
import { Button } from "../../components/ui/button"
import { Badge } from "../../components/ui/badge"
import { Slider } from "../../components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select"
import { Label } from "../../components/ui/label"
import {
  Play,
  Square,
  RotateCcw,
  Settings,
  Wifi,
  WifiOff,
  Activity,
  Zap,
  Clock,
  Target,
  Cpu,
  Usb,
  RefreshCw,
} from "lucide-react"
import { ProstheticViewer } from "../../components/prosthetic-viewer"
import { EmgSignalChart } from "../../components/emg-signal-chart"

export default function LabPage() {
  const [isRecording, setIsRecording] = useState(false)
  const [sessionTime, setSessionTime] = useState(0)
  const [sensitivity, setSensitivity] = useState([75])
  const [deviceType, setDeviceType] = useState<string>("")
  const [selectedPort, setSelectedPort] = useState<string>("")
  const [isConnected, setIsConnected] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const [availablePorts, setAvailablePorts] = useState<string[]>([])

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>
    if (isRecording) {
      interval = setInterval(() => {
        setSessionTime((prev) => prev + 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isRecording])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const handleScanPorts = () => {
    setIsScanning(true)
    setTimeout(() => {
      if (deviceType === "esp32") {
        setAvailablePorts(["192.168.1.100", "192.168.1.101", "192.168.1.105"])
      } else if (deviceType === "arduino") {
        setAvailablePorts(["COM3", "COM4", "/dev/ttyUSB0"])
      } else if (deviceType === "raspberry") {
        setAvailablePorts(["192.168.1.50", "raspberrypi.local"])
      }
      setIsScanning(false)
    }, 1500)
  }

  const handleConnect = () => {
    if (selectedPort) {
      setIsConnected(true)
    }
  }

  const handleDisconnect = () => {
    setIsConnected(false)
    setIsRecording(false)
    setSessionTime(0)
  }

  const getDeviceIcon = () => {
    switch (deviceType) {
      case "esp32":
        return <Wifi className="size-4" />
      case "arduino":
        return <Usb className="size-4" />
      case "raspberry":
        return <Cpu className="size-4" />
      default:
        return <Cpu className="size-4" />
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Capture Lab</h1>
          <p className="text-muted-foreground">Real-time EMG capture and prosthetic control</p>
        </div>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Badge variant="default" className="gap-1">
              <Wifi className="size-3" />
              Connected to {selectedPort}
            </Badge>
          ) : (
            <Badge variant="secondary" className="gap-1">
              <WifiOff className="size-3" />
              Disconnected
            </Badge>
          )}
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid gap-4 lg:grid-cols-4">
        {/* Left Panel - Controls */}
        <div className="space-y-4">
          {/* Device Configuration */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Cpu className="size-4" />
                Device Configuration
              </CardTitle>
              <CardDescription>Connect to your prosthetic device</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Device Type</Label>
                <Select
                  value={deviceType}
                  onValueChange={(value) => {
                    setDeviceType(value)
                    setAvailablePorts([])
                    setSelectedPort("")
                    setIsConnected(false)
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select device type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="esp32">
                      <div className="flex items-center gap-2">
                        <Wifi className="size-4" />
                        ESP32 (WiFi)
                      </div>
                    </SelectItem>
                    <SelectItem value="arduino">
                      <div className="flex items-center gap-2">
                        <Usb className="size-4" />
                        Arduino (Serial)
                      </div>
                    </SelectItem>
                    <SelectItem value="raspberry">
                      <div className="flex items-center gap-2">
                        <Cpu className="size-4" />
                        Raspberry Pi
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {deviceType && (
                <>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>{deviceType === "arduino" ? "Port" : "IP Address"}</Label>
                      <Button variant="ghost" size="sm" onClick={handleScanPorts} disabled={isScanning || isConnected}>
                        <RefreshCw className={`size-3 mr-1 ${isScanning ? "animate-spin" : ""}`} />
                        Scan
                      </Button>
                    </div>
                    <Select value={selectedPort} onValueChange={setSelectedPort} disabled={isConnected}>
                      <SelectTrigger>
                        <SelectValue placeholder={isScanning ? "Scanning..." : "Select port/address"} />
                      </SelectTrigger>
                      <SelectContent>
                        {availablePorts.map((port) => (
                          <SelectItem key={port} value={port}>
                            <div className="flex items-center gap-2">
                              {getDeviceIcon()}
                              {port}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {!isConnected ? (
                    <Button className="w-full" onClick={handleConnect} disabled={!selectedPort}>
                      <Wifi className="size-4 mr-2" />
                      Connect
                    </Button>
                  ) : (
                    <Button variant="destructive" className="w-full" onClick={handleDisconnect}>
                      <WifiOff className="size-4 mr-2" />
                      Disconnect
                    </Button>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Session Controls */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Settings className="size-4" />
                Session Controls
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-center gap-2">
                <Button
                  size="lg"
                  variant={isRecording ? "destructive" : "default"}
                  onClick={() => setIsRecording(!isRecording)}
                  disabled={!isConnected}
                >
                  {isRecording ? (
                    <>
                      <Square className="mr-2 size-4" />
                      Stop
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 size-4" />
                      Start
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => setSessionTime(0)}
                  disabled={isRecording || !isConnected}
                >
                  <RotateCcw className="size-4" />
                </Button>
              </div>

              <div className="rounded-lg border border-border bg-muted/30 p-4 text-center">
                <p className="text-sm text-muted-foreground">Session Time</p>
                <p className="text-3xl font-mono font-bold">{formatTime(sessionTime)}</p>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Sensitivity</Label>
                  <span className="text-sm text-muted-foreground">{sensitivity[0]}%</span>
                </div>
                <Slider value={sensitivity} onValueChange={setSensitivity} max={100} step={1} disabled={!isConnected} />
              </div>
            </CardContent>
          </Card>

          {/* Live Metrics */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Live Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="flex items-center gap-2">
                  <Activity className="size-4 text-primary" />
                  <span className="text-sm">Latency</span>
                </div>
                <span className="font-mono font-medium">{isConnected ? "12ms" : "--"}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="flex items-center gap-2">
                  <Target className="size-4 text-chart-1" />
                  <span className="text-sm">Accuracy</span>
                </div>
                <span className="font-mono font-medium">{isConnected ? "96.2%" : "--"}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="flex items-center gap-2">
                  <Zap className="size-4 text-chart-2" />
                  <span className="text-sm">Fatigue</span>
                </div>
                <span className="font-mono font-medium">{isConnected ? "23%" : "--"}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg border border-border p-3">
                <div className="flex items-center gap-2">
                  <Clock className="size-4 text-chart-3" />
                  <span className="text-sm">Sample Rate</span>
                </div>
                <span className="font-mono font-medium">{isConnected ? "1kHz" : "--"}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Center - 3D Viewer */}
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>3D Prosthetic Viewer</CardTitle>
                  <CardDescription>Real-time visualization of prosthetic movement</CardDescription>
                </div>
                <Badge variant={isRecording ? "default" : "secondary"}>{isRecording ? "Recording" : "Idle"}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <ProstheticViewer isActive={isConnected && isRecording} />
            </CardContent>
          </Card>
        </div>

        {/* Right Panel - EMG Signals */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">EMG Channel 1</CardTitle>
              <CardDescription>Flexor digitorum</CardDescription>
            </CardHeader>
            <CardContent>
              <EmgSignalChart channelId={1} isActive={isConnected && isRecording} color="var(--primary)" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">EMG Channel 2</CardTitle>
              <CardDescription>Extensor digitorum</CardDescription>
            </CardHeader>
            <CardContent>
              <EmgSignalChart channelId={2} isActive={isConnected && isRecording} color="var(--chart-1)" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">EMG Channel 3</CardTitle>
              <CardDescription>Biceps brachii</CardDescription>
            </CardHeader>
            <CardContent>
              <EmgSignalChart channelId={3} isActive={isConnected && isRecording} color="var(--chart-2)" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">EMG Channel 4</CardTitle>
              <CardDescription>Triceps brachii</CardDescription>
            </CardHeader>
            <CardContent>
              <EmgSignalChart channelId={4} isActive={isConnected && isRecording} color="var(--chart-3)" />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
