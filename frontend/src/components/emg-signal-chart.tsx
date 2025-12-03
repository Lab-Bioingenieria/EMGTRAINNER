"use client"

import { ChartContainer, ChartTooltip, ChartTooltipContent } from "./ui/chart"
import { Line, LineChart, XAxis, YAxis } from "recharts"
import { useEffect, useState } from "react"

interface EmgSignalChartProps {
  channelId: number
  isActive: boolean
  color: string
}

export function EmgSignalChart({ channelId, isActive, color }: EmgSignalChartProps) {
  const [data, setData] = useState<{ time: number; value: number }[]>([])

  useEffect(() => {
    if (!isActive) {
      return
    }

    const interval = setInterval(() => {
      setData((prev) => {
        const newData = [...prev]
        const timestamp = Date.now()

        // Different wave patterns per channel
        const baseValue = Math.sin(timestamp / (200 + channelId * 50)) * 50
        const noise = Math.random() * 20 - 10

        newData.push({
          time: timestamp,
          value: baseValue + noise,
        })

        if (newData.length > 50) {
          newData.shift()
        }

        return newData
      })
    }, 50)

    return () => clearInterval(interval)
  }, [isActive, channelId])

  // Reset data when not active
  useEffect(() => {
    if (!isActive) {
      setData([])
    }
  }, [isActive])

  const chartConfig = {
    value: {
      label: `Channel ${channelId}`,
      color: color,
    },
  }

  return (
    <ChartContainer config={chartConfig} className="h-[80px] w-full">
      <LineChart data={data}>
        <XAxis dataKey="time" hide />
        <YAxis hide domain={[-80, 80]} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
      </LineChart>
    </ChartContainer>
  )
}

export { EmgSignalChart as EMGSignalChart }
