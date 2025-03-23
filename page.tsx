import type { Metadata } from "next"
import StudyDashboard from "@/components/study-dashboard"

export const metadata: Metadata = {
  title: "AI Study Website",
  description: "A comprehensive study platform with timer, grades, planner, and study tools",
}

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <StudyDashboard />
    </main>
  )
}


