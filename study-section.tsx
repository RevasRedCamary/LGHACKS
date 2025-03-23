"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Search, BookOpen, FileText, Brain, Lightbulb } from "lucide-react"

export default function StudySection() {
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("resources")
  const [flashcards, setFlashcards] = useState([
    { id: "1", question: "What is the Pythagorean theorem?", answer: "a² + b² = c²" },
    {
      id: "2",
      question: "What is photosynthesis?",
      answer:
        "The process by which green plants and some other organisms use sunlight to synthesize foods with the help of chlorophyll.",
    },
  ])
  const [newFlashcard, setNewFlashcard] = useState({ question: "", answer: "" })
  const [showingAnswer, setShowingAnswer] = useState<Record<string, boolean>>({})

  const resources = [
    {
      title: "Introduction to Calculus",
      type: "PDF",
      description: "Comprehensive guide to calculus fundamentals",
      link: "#",
    },
    {
      title: "Chemistry Lab Techniques",
      type: "Video",
      description: "Visual demonstrations of common lab procedures",
      link: "#",
    },
    {
      title: "World History Timeline",
      type: "Interactive",
      description: "Interactive timeline of major historical events",
      link: "#",
    },
  ]

  const notes = [
    {
      id: "1",
      title: "Biology Chapter 5 Notes",
      content: "Cell structure and function: The cell membrane is a phospholipid bilayer...",
      date: "2023-05-10",
    },
    {
      id: "2",
      title: "Physics Formulas",
      content: "F = ma (Force = mass × acceleration)\nE = mc² (Energy = mass × speed of light²)",
      date: "2023-05-15",
    },
  ]

  const addFlashcard = () => {
    if (!newFlashcard.question || !newFlashcard.answer) return

    setFlashcards([
      ...flashcards,
      {
        id: Date.now().toString(),
        question: newFlashcard.question,
        answer: newFlashcard.answer,
      },
    ])

    setNewFlashcard({ question: "", answer: "" })
  }

  const toggleAnswer = (id: string) => {
    setShowingAnswer({
      ...showingAnswer,
      [id]: !showingAnswer[id],
    })
  }

  const filteredResources = resources.filter(
    (resource) =>
      resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      resource.description.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const filteredNotes = notes.filter(
    (note) =>
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.content.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const filteredFlashcards = flashcards.filter(
    (card) =>
      card.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      card.answer.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search resources, notes, and flashcards..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <Tabs defaultValue="resources" onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-3 mb-4">
          <TabsTrigger value="resources">
            <BookOpen className="mr-2 h-4 w-4" />
            Resources
          </TabsTrigger>
          <TabsTrigger value="notes">
            <FileText className="mr-2 h-4 w-4" />
            Notes
          </TabsTrigger>
          <TabsTrigger value="flashcards">
            <Brain className="mr-2 h-4 w-4" />
            Flashcards
          </TabsTrigger>
        </TabsList>

        <TabsContent value="resources" className="space-y-4">
          <h3 className="text-lg font-medium">Study Resources</h3>
          {filteredResources.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredResources.map((resource, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium">{resource.title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">{resource.description}</p>
                        <div className="mt-2">
                          <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                            {resource.type}
                          </span>
                        </div>
                      </div>
                      <Button variant="outline" size="sm" asChild>
                        <a href={resource.link} target="_blank" rel="noopener noreferrer">
                          Open
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 text-muted-foreground">
              No resources found. Try a different search term.
            </div>
          )}
        </TabsContent>

        <TabsContent value="notes" className="space-y-4">
          <h3 className="text-lg font-medium">Study Notes</h3>
          {filteredNotes.length > 0 ? (
            <Accordion type="single" collapsible className="w-full">
              {filteredNotes.map((note) => (
                <AccordionItem key={note.id} value={note.id}>
                  <AccordionTrigger>
                    <div className="flex flex-col items-start">
                      <div>{note.title}</div>
                      <div className="text-xs text-muted-foreground">{note.date}</div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="whitespace-pre-line">{note.content}</div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          ) : (
            <div className="text-center py-6 text-muted-foreground">No notes found. Try a different search term.</div>
          )}
        </TabsContent>

        <TabsContent value="flashcards" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium mb-4">Create Flashcard</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="question">Question</Label>
                  <Textarea
                    id="question"
                    placeholder="Enter your question"
                    value={newFlashcard.question}
                    onChange={(e) =>
                      setNewFlashcard({
                        ...newFlashcard,
                        question: e.target.value,
                      })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="answer">Answer</Label>
                  <Textarea
                    id="answer"
                    placeholder="Enter the answer"
                    value={newFlashcard.answer}
                    onChange={(e) =>
                      setNewFlashcard({
                        ...newFlashcard,
                        answer: e.target.value,
                      })
                    }
                  />
                </div>
                <Button onClick={addFlashcard} className="w-full">
                  <Lightbulb className="mr-2 h-4 w-4" />
                  Add Flashcard
                </Button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-4">Flashcards</h3>
              {filteredFlashcards.length > 0 ? (
                <div className="space-y-4">
                  {filteredFlashcards.map((card) => (
                    <Card key={card.id} className="overflow-hidden">
                      <div className="p-4 cursor-pointer" onClick={() => toggleAnswer(card.id)}>
                        <div className="font-medium mb-2">{card.question}</div>
                        {showingAnswer[card.id] && (
                          <div className="mt-2 pt-2 border-t">
                            <div className="text-sm text-muted-foreground mb-1">Answer:</div>
                            <div>{card.answer}</div>
                          </div>
                        )}
                        {!showingAnswer[card.id] && (
                          <div className="text-sm text-muted-foreground">Click to reveal answer</div>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-muted-foreground">
                  No flashcards found. Try a different search term or create new flashcards.
                </div>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}


