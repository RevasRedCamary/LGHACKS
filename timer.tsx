
"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Play, Pause, RotateCcw, Settings } from "lucide-react"
import { Slider } from "@/components/ui/slider"

export default function Timer() {
  const [mode, setMode] = useState<"pomodoro" | "shortBreak" | "longBreak">("pomodoro")
  const [isRunning, setIsRunning] = useState(false)
  const [timeLeft, setTimeLeft] = useState(25 * 60) // 25 minutes in seconds
  const [showSettings, setShowSettings] = useState(false)
  const [settings, setSettings] = useState({
    pomodoro: 25,
    shortBreak: 5,
    longBreak: 15,
  })

  useEffect(() => {
    let timer: NodeJS.Timeout

    if (isRunning && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1)
      }, 1000)
    } else if (timeLeft === 0) {
      setIsRunning(false)
      // Play notification sound or show alert
    }

    return () => clearInterval(timer)
  }, [isRunning, timeLeft])

  useEffect(() => {
    // Reset timer when mode changes
    switch (mode) {
      case "pomodoro":
        setTimeLeft(settings.pomodoro * 60)
        break
      case "shortBreak":
        setTimeLeft(settings.shortBreak * 60)
        break
      case "longBreak":
        setTimeLeft(settings.longBreak * 60)
        break
    }
    setIsRunning(false)
  }, [mode, settings])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const handleStartPause = () => {
    setIsRunning(!isRunning)
  }

  const handleReset = () => {
    switch (mode) {
      case "pomodoro":
        setTimeLeft(settings.pomodoro * 60)
        break
      case "shortBreak":
        setTimeLeft(settings.shortBreak * 60)
        break
      case "longBreak":
        setTimeLeft(settings.longBreak * 60)
        break
    }
    setIsRunning(false)
  }

  const updateSetting = (key: keyof typeof settings, value: number[]) => {
    setSettings({
      ...settings,
      [key]: value[0],
    })
  }

  return (
    <div className="max-w-md mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Focus Timer</CardTitle>
            <Button variant="ghost" size="icon" onClick={() => setShowSettings(!showSettings)}>
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {showSettings ? (
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Pomodoro: {settings.pomodoro} minutes</label>
                <Slider
                  value={[settings.pomodoro]}
                  min={5}
                  max={60}
                  step={1}
                  onValueChange={(value) => updateSetting("pomodoro", value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Short Break: {settings.shortBreak} minutes</label>
                <Slider
                  value={[settings.shortBreak]}
                  min={1}
                  max={15}
                  step={1}
                  onValueChange={(value) => updateSetting("shortBreak", value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Long Break: {settings.longBreak} minutes</label>
                <Slider
                  value={[settings.longBreak]}
                  min={5}
                  max={30}
                  step={1}
                  onValueChange={(value) => updateSetting("longBreak", value)}
                />
              </div>
              <Button className="w-full" onClick={() => setShowSettings(false)}>
                Save Settings
              </Button>
            </div>
          ) : (
            <>
              <Tabs defaultValue="pomodoro" className="mb-6" onValueChange={(value) => setMode(value as any)}>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="pomodoro">Pomodoro</TabsTrigger>
                  <TabsTrigger value="shortBreak">Short Break</TabsTrigger>
                  <TabsTrigger value="longBreak">Long Break</TabsTrigger>
                </TabsList>
              </Tabs>

              <div className="text-center mb-8">
                <div className="text-6xl font-bold mb-6">{formatTime(timeLeft)}</div>
                <div className="flex justify-center gap-4">
                  <Button onClick={handleStartPause}>
                    {isRunning ? <Pause className="mr-2 h-4 w-4" /> : <Play className="mr-2 h-4 w-4" />}
                    {isRunning ? "Pause" : "Start"}
                  </Button>
                  <Button variant="outline" onClick={handleReset}>
                    <RotateCcw className="mr-2 h-4 w-4" />
                    Reset
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

