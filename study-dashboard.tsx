
"use client"

import { useState } from "react"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Cookie } from "lucide-react"
import Timer from "@/components/timer"
import Grades from "@/components/grades"
import Planner from "@/components/planner"
import StudySection from "@/components/study-section"

type Section = "timer" | "grades" | "planner" | "study"

export default function StudyDashboard() {
  const [activeSection, setActiveSection] = useState<Section>("timer")

  const renderSection = () => {
    switch (activeSection) {
      case "timer":
        return <Timer />
      case "grades":
        return <Grades />
      case "planner":
        return <Planner />
      case "study":
        return <StudySection />
      default:
        return <Timer />
    }
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center justify-between mb-8">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" className="rounded-full">
              <Cookie className="h-6 w-6" />
              <span className="sr-only">Open menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[250px] sm:w-[300px]">
            <nav className="flex flex-col gap-4 mt-8">
              <Button
                variant={activeSection === "timer" ? "default" : "ghost"}
                className="justify-start"
                onClick={() => setActiveSection("timer")}
              >
                Timer
              </Button>
              <Button
                variant={activeSection === "grades" ? "default" : "ghost"}
                className="justify-start"
                onClick={() => setActiveSection("grades")}
              >
                Grades
              </Button>
              <Button
                variant={activeSection === "planner" ? "default" : "ghost"}
                className="justify-start"
                onClick={() => setActiveSection("planner")}
              >
                Planner
              </Button>
              <Button
                variant={activeSection === "study" ? "default" : "ghost"}
                className="justify-start"
                onClick={() => setActiveSection("study")}
              >
                Study
              </Button>
            </nav>
          </SheetContent>
        </Sheet>
        <h1 className="text-2xl font-bold">AI Study Website</h1>
        <div className="w-10" />
      </div>

      <div className="bg-card rounded-lg shadow-lg p-6 min-h-[calc(100vh-150px)]">{renderSection()}</div>
    </div>
  )
}

