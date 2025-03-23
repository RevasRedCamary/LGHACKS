
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { format } from "date-fns"
import { CalendarIcon, PlusCircle, Trash2, CheckCircle2 } from "lucide-react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { cn } from "@/lib/utils"

type Task = {
  id: string
  title: string
  description: string
  date: Date
  priority: "low" | "medium" | "high"
  completed: boolean
}

export default function Planner() {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: "1",
      title: "Complete Math Assignment",
      description: "Finish problems 1-20 for Chapter 5",
      date: new Date(2023, 5, 15),
      priority: "high",
      completed: false,
    },
    {
      id: "2",
      title: "Study for Science Quiz",
      description: "Review chapters 3 and 4",
      date: new Date(2023, 5, 18),
      priority: "medium",
      completed: true,
    },
  ])

  const [newTask, setNewTask] = useState<Omit<Task, "id" | "completed">>({
    title: "",
    description: "",
    date: new Date(),
    priority: "medium",
  })

  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date())

  const addTask = () => {
    if (!newTask.title || !newTask.date) {
      return
    }

    setTasks([
      ...tasks,
      {
        ...newTask,
        id: Date.now().toString(),
        completed: false,
      },
    ])

    setNewTask({
      title: "",
      description: "",
      date: new Date(),
      priority: "medium",
    })
  }

  const deleteTask = (id: string) => {
    setTasks(tasks.filter((task) => task.id !== id))
  }

  const toggleTaskCompletion = (id: string) => {
    setTasks(tasks.map((task) => (task.id === id ? { ...task, completed: !task.completed } : task)))
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "text-red-500"
      case "medium":
        return "text-yellow-500"
      case "low":
        return "text-green-500"
      default:
        return ""
    }
  }

  const filteredTasks = selectedDate
    ? tasks.filter(
        (task) =>
          task.date.getDate() === selectedDate.getDate() &&
          task.date.getMonth() === selectedDate.getMonth() &&
          task.date.getFullYear() === selectedDate.getFullYear(),
      )
    : tasks

  // Function to get dates with tasks for the calendar
  const getTaskDates = () => {
    return tasks.map((task) => task.date)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Study Planner</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium mb-4">Add New Task</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Task Title</Label>
                  <Input
                    id="title"
                    placeholder="e.g., Complete Math Assignment"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="e.g., Finish problems 1-20 for Chapter 5"
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="date">Due Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left font-normal">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {newTask.date ? format(newTask.date, "PPP") : <span>Pick a date</span>}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={newTask.date}
                        onSelect={(date) => setNewTask({ ...newTask, date: date || new Date() })}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select
                    value={newTask.priority}
                    onValueChange={(value: any) => setNewTask({ ...newTask, priority: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={addTask} className="w-full">
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Add Task
                </Button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-4">Calendar</h3>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={setSelectedDate}
                className="rounded-md border"
                modifiers={{
                  hasTasks: getTaskDates(),
                }}
                modifiersStyles={{
                  hasTasks: {
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                    fontWeight: "bold",
                  },
                }}
              />
              <div className="mt-4 text-sm text-center text-muted-foreground">
                {selectedDate ? `Tasks for ${format(selectedDate, "MMMM d, yyyy")}` : "Select a date to view tasks"}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{selectedDate ? `Tasks for ${format(selectedDate, "MMMM d, yyyy")}` : "All Tasks"}</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredTasks.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50px]">Status</TableHead>
                  <TableHead>Task</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTasks.map((task) => (
                  <TableRow key={task.id} className={cn(task.completed && "opacity-60")}>
                    <TableCell>
                      <Button variant="ghost" size="icon" onClick={() => toggleTaskCompletion(task.id)}>
                        <CheckCircle2
                          className={cn(
                            "h-5 w-5",
                            task.completed ? "text-green-500 fill-green-500" : "text-muted-foreground",
                          )}
                        />
                      </Button>
                    </TableCell>
                    <TableCell>
                      <div className={cn(task.completed && "line-through")}>
                        <div className="font-medium">{task.title}</div>
                        <div className="text-sm text-muted-foreground">{task.description}</div>
                      </div>
                    </TableCell>
                    <TableCell>{format(task.date, "MMM d, yyyy")}</TableCell>
                    <TableCell>
                      <span className={getPriorityColor(task.priority)}>
                        {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => deleteTask(task.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-6 text-muted-foreground">
              {selectedDate
                ? "No tasks scheduled for this date."
                : "No tasks added yet. Add your first task to get started."}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

