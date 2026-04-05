import { useState } from 'react'
import { Sparkles, Box, Send, Command } from 'lucide-react'
import { executeAICommand } from '../api/mcp'

interface Message {
    type: 'user' | 'system'
    content: string
}

export default function AIConstructor() {
    const [prompt, setPrompt] = useState('')
    const [history, setHistory] = useState<Message[]>([])
    const [processing, setProcessing] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!prompt.trim() || processing) return

        const userPrompt = prompt.trim()
        setHistory(prev => [...prev, { type: 'user', content: userPrompt }])
        setPrompt('')
        setProcessing(true)

        try {
            const response = await executeAICommand(userPrompt)
            if (response.success && response.data) {
                setHistory(prev => [...prev, { 
                    type: 'system', 
                    content: response.data?.result || 'Command executed successfully'
                }])
            } else {
                setHistory(prev => [...prev, { 
                    type: 'system', 
                    content: `Error: ${response.error || 'Failed to execute command'}` 
                }])
            }
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Unknown error'
            setHistory(prev => [...prev, { type: 'system', content: `Error: ${errorMsg}` }])
        } finally {
            setProcessing(false)
        }
    }

    return (
        <div className="p-6 max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
            <div className="mb-6">
                <h1 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
                    <Sparkles className="w-6 h-6 text-purple-400" />
                    AI Constructor
                </h1>
                <p className="text-muted-foreground">Generate objects and scenes using natural language.</p>
            </div>

            <div className="flex-1 bg-card border border-border rounded-lg shadow-sm flex flex-col overflow-hidden">
                <div className="flex-1 p-4 overflow-y-auto space-y-4">
                    {history.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50">
                            <Box className="w-16 h-16 mb-4" />
                            <p>Type a command to start building...</p>
                        </div>
                    )}

                    {history.map((msg, i) => (
                        <div key={i} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div
                                className={`max-w-[80%] px-4 py-2 rounded-lg ${msg.type === 'user'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-muted text-muted-foreground'
                                    }`}
                            >
                                {msg.type === 'system' && <Command className="w-3 h-3 inline mr-2 opacity-70" />}
                                {msg.content}
                            </div>
                        </div>
                    ))}
                    {processing && (
                        <div className="flex justify-start">
                            <div className="bg-muted text-muted-foreground px-4 py-2 rounded-lg flex items-center space-x-2">
                                <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
                                <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.2s]" />
                                <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.4s]" />
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-4 border-t border-border bg-muted/20">
                    <form onSubmit={handleSubmit} className="flex gap-2">
                        <input
                            type="text"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="Describe what you want to create (e.g., 'A modern chair with wooden legs')..."
                            className="flex-1 bg-background border border-input rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-ring"
                            disabled={processing}
                        />
                        <button
                            type="submit"
                            disabled={processing || !prompt.trim()}
                            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </form>
                </div>
            </div>

            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                {['Create a forest', 'Add a sunlight', 'Make it night', 'Render scene'].map((suggestion) => (
                    <button
                        key={suggestion}
                        onClick={() => setPrompt(suggestion)}
                        className="text-xs text-muted-foreground border border-border rounded px-3 py-2 hover:bg-accent hover:text-accent-foreground transition-colors text-left"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
        </div>
    )
}
