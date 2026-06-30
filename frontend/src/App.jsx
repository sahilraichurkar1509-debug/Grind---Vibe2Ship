import { useState } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

export default function App() {
  const [task, setTask] = useState("")
  const [deadline, setDeadline] = useState("")
  const [breakdown, setBreakdown] = useState(null)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [pendingTasks, setPendingTasks] = useState([])
  const [panicMode, setPanicMode] = useState(false)

  const handleBreakdown = async () => {
    if (!task || !deadline) return
    setLoading(true)
    try {
      const res = await axios.post(`${API}/tasks/breakdown`, { task, deadline })
      const data = res.data.breakdown
      setBreakdown(data)
      setPendingTasks(prev => [...prev, { task, deadline, subtasks: data.subtasks }])
      const hoursLeft = (new Date(deadline) - new Date()) / 1000 / 3600
      setPanicMode(hoursLeft < 24)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const handleReplan = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API}/tasks/replan`, pendingTasks)
      setPlan(res.data.plan)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  return (
    <div className={`min-h-screen ${panicMode ? "bg-red-950" : "bg-gray-950"} text-white p-6`}>
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">lightning</span>
          <h1 className="text-3xl font-bold">LastMinute AI</h1>
          {panicMode && (
            <span className="bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full animate-pulse">
              PANIC MODE
            </span>
          )}
        </div>
        <p className="text-gray-400 mb-8">Your AI-powered study companion for Indian college students</p>

        <div className="bg-gray-900 rounded-2xl p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Add a Task</h2>
          <input
            className="w-full bg-gray-800 rounded-xl px-4 py-3 mb-3 text-white placeholder-gray-500 outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g. Prepare for DSA exam, Submit OS assignment..."
            value={task}
            onChange={e => setTask(e.target.value)}
          />
          <input
            type="date"
            className="w-full bg-gray-800 rounded-xl px-4 py-3 mb-4 text-white outline-none focus:ring-2 focus:ring-blue-500"
            value={deadline}
            onChange={e => setDeadline(e.target.value)}
          />
          <button
            onClick={handleBreakdown}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-xl py-3 font-semibold transition"
          >
            {loading ? "Gemini is thinking..." : "Break it down with AI"}
          </button>
        </div>

        {breakdown && !breakdown.error && (
          <div className={`rounded-2xl p-6 mb-6 ${panicMode ? "bg-red-900 border border-red-500" : "bg-gray-900"}`}>
            <h2 className="text-lg font-semibold mb-1">{breakdown.task_name}</h2>
            <p className="text-gray-400 text-sm mb-4">{breakdown.reasoning}</p>
            <div className="space-y-2">
              {breakdown.subtasks && breakdown.subtasks.map((s, i) => (
                <div key={i} className="flex items-center justify-between bg-gray-800 rounded-xl px-4 py-3">
                  <span>{s.name}</span>
                  <span className="text-blue-400 text-sm font-medium">{s.duration_minutes} min</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-700 flex justify-between text-sm text-gray-400">
              <span>Total time needed</span>
              <span className="text-white font-semibold">
                {breakdown.subtasks && breakdown.subtasks.reduce((a, b) => a + b.duration_minutes, 0)} min
              </span>
            </div>
          </div>
        )}

        {pendingTasks.length > 0 && (
          <div className="bg-gray-900 rounded-2xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Pending Tasks ({pendingTasks.length})</h2>
              <button
                onClick={handleReplan}
                disabled={loading}
                className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 px-4 py-2 rounded-xl text-sm font-semibold transition"
              >
                {loading ? "Planning..." : "Replan my day"}
              </button>
            </div>
            <div className="space-y-2">
              {pendingTasks.map((t, i) => (
                <div key={i} className="flex items-center justify-between bg-gray-800 rounded-xl px-4 py-3">
                  <span>{t.task}</span>
                  <span className="text-gray-400 text-sm">{t.deadline}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {plan && !plan.error && (
          <div className="bg-gray-900 rounded-2xl p-6 mb-6">
            <h2 className="text-lg font-semibold mb-1">Your AI Plan for Today</h2>
            <p className="text-gray-400 text-sm mb-4">{plan.reasoning}</p>
            <div className="space-y-2">
              {plan.plan && plan.plan.map((p, i) => (
                <div key={i} className="flex items-center gap-4 bg-gray-800 rounded-xl px-4 py-3">
                  <span className="text-blue-400 font-mono text-sm w-14">{p.start_time}</span>
                  <span className="flex-1">{p.task}</span>
                  <span className="text-gray-400 text-sm">{p.duration_minutes}m</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Google Calendar integration removed for student-focused build */}
      </div>
    </div>
  )
}
