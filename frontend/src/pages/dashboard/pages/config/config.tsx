import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../../components/ui/card"
import { Button } from "../../../../components/ui/button"
import { Badge } from "../../../../components/ui/badge"
import { Alert, AlertDescription } from "../../../../components/ui/alert"
import { Cpu, Wifi, WifiOff, Plus, Trash2, Power } from "lucide-react"

interface Device {
  id: string
  name: string
  type: "ESP32" | "Arduino" | "RaspberryPi"
  port: string
  baudRate: number
  status: "connected" | "disconnected"
  lastConnected: string
}

export default function DeviceConfigPage() {
  const [devices, setDevices] = useState<Device[]>([
    {
      id: "1",
      name: "Prosthetic Unit #01",
      type: "ESP32",
      port: "/dev/ttyUSB0",
      baudRate: 115200,
      status: "connected",
      lastConnected: "Now",
    },
  ])

  const [deviceIdCounter, setDeviceIdCounter] = useState(2)
  const [showAddDevice, setShowAddDevice] = useState(false)
  const [selectedDeviceType, setSelectedDeviceType] = useState<"ESP32" | "Arduino" | "RaspberryPi" | null>(null)
  const [newDeviceName, setNewDeviceName] = useState("")
  const [newDevicePort, setNewDevicePort] = useState("")
  const [newDeviceBaudRate, setNewDeviceBaudRate] = useState("115200")

  const deviceTypes = [
    {
      type: "ESP32",
      description: "Microcontroller with Wi-Fi and Bluetooth",
      baudRates: [9600, 115200, 921600],
      icon: "📡",
    },
    {
      type: "Arduino",
      description: "Traditional Arduino boards with USB serial",
      baudRates: [9600, 19200, 57600, 115200],
      icon: "🔌",
    },
    {
      type: "RaspberryPi",
      description: "Single-board computer with GPIO support",
      baudRates: [115200, 460800],
      icon: "🍓",
    },
  ]

  const toggleDeviceConnection = (id: string) => {
    setDevices(
      devices.map((device) =>
        device.id === id ? { ...device, status: device.status === "connected" ? "disconnected" : "connected" } : device,
      ),
    )
  }

  const removeDevice = (id: string) => {
    setDevices(devices.filter((device) => device.id !== id))
  }

  const addDevice = () => {
    if (!selectedDeviceType || !newDeviceName || !newDevicePort) return

    const newDevice: Device = {
      id: deviceIdCounter.toString(),
      name: newDeviceName,
      type: selectedDeviceType,
      port: newDevicePort,
      baudRate: Number.parseInt(newDeviceBaudRate),
      status: "disconnected",
      lastConnected: "Never",
    }

    setDevices([...devices, newDevice])
    setDeviceIdCounter((prev) => prev + 1)
    resetForm()
  }

  const resetForm = () => {
    setShowAddDevice(false)
    setSelectedDeviceType(null)
    setNewDeviceName("")
    setNewDevicePort("")
    setNewDeviceBaudRate("115200")
  }

  return (
    <div className="p-6 space-y-6">
      {/* Connected Devices */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-foreground">Connected Devices</h2>
          <Button onClick={() => setShowAddDevice(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Add Device
          </Button>
        </div>

        {devices.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-muted-foreground">No devices configured yet</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {devices.map((device) => (
              <Card key={device.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        {device.type === "ESP32" && "📡"}
                        {device.type === "Arduino" && "🔌"}
                        {device.type === "RaspberryPi" && "🍓"}
                      </div>
                      <div>
                        <CardTitle className="text-base">{device.name}</CardTitle>
                        <CardDescription className="text-xs">
                          {device.type} • {device.port}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {device.status === "connected" ? (
                        <Badge variant="default" className="bg-green-600 gap-1">
                          <Wifi className="w-3 h-3" />
                          Connected
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="gap-1">
                          <WifiOff className="w-3 h-3" />
                          Disconnected
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-muted-foreground">Baud Rate</p>
                      <p className="text-sm font-medium">{device.baudRate}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Port</p>
                      <p className="text-sm font-medium font-mono">{device.port}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Last Connected</p>
                      <p className="text-sm font-medium">{device.lastConnected}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Status</p>
                      <p className="text-sm font-medium capitalize">{device.status}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant={device.status === "connected" ? "destructive" : "default"}
                      size="sm"
                      onClick={() => toggleDeviceConnection(device.id)}
                      className="gap-2"
                    >
                      <Power className="w-4 h-4" />
                      {device.status === "connected" ? "Disconnect" : "Connect"}
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => removeDevice(device.id)} className="gap-2">
                      <Trash2 className="w-4 h-4" />
                      Remove
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Add New Device Form */}
      {showAddDevice && (
        <Card className="border-primary/50 bg-primary/5">
          <CardHeader>
            <CardTitle>Add New Device</CardTitle>
            <CardDescription>Configure a new device for data collection</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!selectedDeviceType ? (
              <div>
                <p className="text-sm font-medium mb-3">Select Device Type</p>
                <div className="grid md:grid-cols-3 gap-3">
                  {deviceTypes.map((device) => (
                    <button
                      key={device.type}
                      onClick={() => setSelectedDeviceType(device.type as "ESP32" | "Arduino" | "RaspberryPi")}
                      className="p-4 border border-border rounded-lg hover:border-primary hover:bg-primary/5 transition-colors text-left"
                    >
                      <p className="text-2xl mb-2">{device.icon}</p>
                      <p className="font-medium text-sm">{device.type}</p>
                      <p className="text-xs text-muted-foreground mt-1">{device.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Device Type</label>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge>{selectedDeviceType}</Badge>
                    <Button variant="ghost" size="sm" onClick={() => setSelectedDeviceType(null)}>
                      Change
                    </Button>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium">Device Name</label>
                  <input
                    type="text"
                    placeholder="e.g., Prosthetic Unit #01"
                    value={newDeviceName}
                    onChange={(e) => setNewDeviceName(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Port</label>
                  <input
                    type="text"
                    placeholder={
                      selectedDeviceType === "RaspberryPi" ? "e.g., 192.168.1.100" : "e.g., /dev/ttyUSB0 or COM3"
                    }
                    value={newDevicePort}
                    onChange={(e) => setNewDevicePort(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Baud Rate</label>
                  <select
                    value={newDeviceBaudRate}
                    onChange={(e) => setNewDeviceBaudRate(e.target.value)}
                    className="w-full mt-1 px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    {deviceTypes
                      .find((d) => d.type === selectedDeviceType)
                      ?.baudRates.map((rate) => (
                        <option key={rate} value={rate}>
                          {rate}
                        </option>
                      ))}
                  </select>
                </div>

                <Alert>
                  <Cpu className="h-4 w-4" />
                  <AlertDescription>
                    Make sure your device is connected via USB or network and properly configured before adding it.
                  </AlertDescription>
                </Alert>

                <div className="flex gap-2">
                  <Button onClick={addDevice} className="flex-1">
                    Add Device
                  </Button>
                  <Button variant="outline" onClick={resetForm} className="flex-1 bg-transparent">
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Device Information */}
      <div className="grid md:grid-cols-3 gap-4">
        {deviceTypes.map((device) => (
          <Card key={device.type}>
            <CardHeader>
              <CardTitle className="text-base">{device.type}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground">{device.description}</p>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Supported Baud Rates:</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {device.baudRates.map((rate) => (
                    <Badge key={rate} variant="outline" className="text-xs">
                      {rate}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

