"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { PlusCircle, Trash2 } from "lucide-react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

type Grade = {
  id: string
  subject: string
  assignment: string
  grade: number
  weight: number
}

export default function Grades() {
  const [grades, setGrades] = useState<Grade[]>([
    {
      id: "1",
      subject: "Mathematics",
      assignment: "Midterm Exam",
      grade: 85,
      weight: 30,
    },
    {
      id: "2",
      subject: "Science",
      assignment: "Lab Report",
      grade: 92,
      weight: 20,
    },
  ])

  const [newGrade, setNewGrade] = useState<Omit<Grade, "id">>({
    subject: "",
    assignment: "",
    grade: 0,
    weight: 0,
  })

  const addGrade = () => {
    if (
      !newGrade.subject ||
      !newGrade.assignment ||
      newGrade.grade < 0 ||
      newGrade.grade > 100 ||
      newGrade.weight <= 0
    ) {
      return
    }

    setGrades([
      ...grades,
      {
        ...newGrade,
        id: Date.now().toString(),
      },
    ])

    setNewGrade({
      subject: "",
      assignment: "",
      grade: 0,
      weight: 0,
    })
  }

  const deleteGrade = (id: string) => {
    setGrades(grades.filter((grade) => grade.id !== id))
  }

  const calculateAverage = (subject?: string) => {
    const filteredGrades = subject ? grades.filter((grade) => grade.subject === subject) : grades

    if (filteredGrades.length === 0) return 0

    const totalWeightedGrade = filteredGrades.reduce((sum, grade) => sum + grade.grade * grade.weight, 0)
    const totalWeight = filteredGrades.reduce((sum, grade) => sum + grade.weight, 0)

    return totalWeight > 0 ? Math.round((totalWeightedGrade / totalWeight) * 100) / 100 : 0
  }

  const getGradeColor = (grade: number) => {
    if (grade >= 90) return "text-green-500"
    if (grade >= 80) return "text-blue-500"
    if (grade >= 70) return "text-yellow-500"
    if (grade >= 60) return "text-orange-500"
    return "text-red-500"
  }

  const getLetterGrade = (grade: number) => {
    if (grade >= 90) return "A"
    if (grade >= 80) return "B"
    if (grade >= 70) return "C"
    if (grade >= 60) return "D"
    return "F"
  }

  const subjects = Array.from(new Set(grades.map((grade) => grade.subject)))

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Grade Tracker</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium mb-4">Add New Grade</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="subject">Subject</Label>
                  <Input
                    id="subject"
                    placeholder="e.g., Mathematics"
                    value={newGrade.subject}
                    onChange={(e) => setNewGrade({ ...newGrade, subject: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="assignment">Assignment</Label>
                  <Input
                    id="assignment"
                    placeholder="e.g., Midterm Exam"
                    value={newGrade.assignment}
                    onChange={(e) => setNewGrade({ ...newGrade, assignment: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="grade">Grade (%)</Label>
                  <Input
                    id="grade"
                    type="number"
                    min="0"
                    max="100"
                    placeholder="e.g., 85"
                    value={newGrade.grade || ""}
                    onChange={(e) =>
                      setNewGrade({
                        ...newGrade,
                        grade: Number(e.target.value),
                      })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="weight">Weight (%)</Label>
                  <Input
                    id="weight"
                    type="number"
                    min="1"
                    placeholder="e.g., 30"
                    value={newGrade.weight || ""}
                    onChange={(e) =>
                      setNewGrade({
                        ...newGrade,
                        weight: Number(e.target.value),
                      })
                    }
                  />
                </div>
                <Button onClick={addGrade} className="w-full">
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Add Grade
                </Button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-4">Grade Summary</h3>
              <div className="space-y-4">
                <div className="p-4 bg-muted rounded-lg">
                  <div className="text-sm text-muted-foreground mb-2">Overall Average</div>
                  <div className={`text-3xl font-bold ${getGradeColor(calculateAverage())}`}>
                    {calculateAverage()}% ({getLetterGrade(calculateAverage())})
                  </div>
                </div>

                {subjects.length > 0 && (
                  <div className="space-y-3">
                    <div className="text-sm font-medium">By Subject</div>
                    {subjects.map((subject) => (
                      <div
                        key={subject}
                        className="flex justify-between items-center p-3 bg-background rounded-md border"
                      >
                        <div>{subject}</div>
                        <div className={`font-medium ${getGradeColor(calculateAverage(subject))}`}>
                          {calculateAverage(subject)}% ({getLetterGrade(calculateAverage(subject))})
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Grade History</CardTitle>
        </CardHeader>
        <CardContent>
          {grades.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Subject</TableHead>
                  <TableHead>Assignment</TableHead>
                  <TableHead>Grade</TableHead>
                  <TableHead>Weight</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {grades.map((grade) => (
                  <TableRow key={grade.id}>
                    <TableCell>{grade.subject}</TableCell>
                    <TableCell>{grade.assignment}</TableCell>
                    <TableCell className={getGradeColor(grade.grade)}>
                      {grade.grade}% ({getLetterGrade(grade.grade)})
                    </TableCell>
                    <TableCell>{grade.weight}%</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => deleteGrade(grade.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-6 text-muted-foreground">
              No grades added yet. Add your first grade to get started.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}


