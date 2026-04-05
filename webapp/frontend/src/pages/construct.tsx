import { useState } from 'react'
import { Wand2, Play, Code, CheckCircle, AlertCircle, Download, Copy } from 'lucide-react'
import { executeScript, generateBlenderScript as apiGenerateBlenderScript, getConfig } from '../api/mcp'

interface GenerationStep {
    id: string
    label: string
    status: 'pending' | 'running' | 'completed' | 'error'
    message?: string
}

export default function Construct() {
    const [prompt, setPrompt] = useState('')
    const [generatedScript, setGeneratedScript] = useState('')
    const [isGenerating, setIsGenerating] = useState(false)
    const [isExecuting, setIsExecuting] = useState(false)
    const [result, setResult] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [steps, setSteps] = useState<GenerationStep[]>([
        { id: 'analyze', label: 'Analyze prompt', status: 'pending' },
        { id: 'generate', label: 'Generate Blender script', status: 'pending' },
        { id: 'execute', label: 'Execute in Blender', status: 'pending' }
    ])

    const updateStep = (id: string, status: GenerationStep['status'], message?: string) => {
        setSteps(prev => prev.map(step =>
            step.id === id ? { ...step, status, message } : step
        ))
    }

    const generateScript = async () => {
        if (!prompt.trim()) return

        setIsGenerating(true)
        setError(null)
        setResult(null)
        setGeneratedScript('')

        updateStep('analyze', 'running')
        await new Promise(r => setTimeout(r, 300))
        updateStep('analyze', 'completed', `Creating: ${prompt}`)

        updateStep('generate', 'running')
        let model = 'llama3.2'
        let ollamaUrl = 'http://localhost:11434'
        try {
            const configRes = await getConfig()
            if (configRes.success && configRes.data?.llm) {
                const llm = configRes.data.llm as { selected_model?: string; ollama_url?: string }
                if (llm.selected_model) model = llm.selected_model
                if (llm.ollama_url) ollamaUrl = llm.ollama_url
            }
        } catch {
            // use defaults
        }
        const response = await apiGenerateBlenderScript(prompt.trim(), model, ollamaUrl)
        if (response.success && response.data?.script) {
            setGeneratedScript(response.data.script)
            updateStep('generate', 'completed', 'Script generated (LLM)')
        } else {
            const err = response.data?.error ?? response.error ?? 'LLM failed. Is Ollama running? Select a model in Settings.'
            updateStep('generate', 'error', err)
            setError(err)
        }
        setIsGenerating(false)
    }

    const runScript = async () => {
        if (!generatedScript) return

        setIsExecuting(true)
        updateStep('execute', 'running')

        try {
            const response = await executeScript(generatedScript)
            if (response.success && response.data) {
                updateStep('execute', 'completed', response.data.output || 'Object created successfully')
                setResult(response.data.output || 'Object created in Blender')
            } else {
                updateStep('execute', 'error', response.error || 'Failed to execute')
                setError(response.error || 'Failed to execute script')
            }
        } catch (err) {
            updateStep('execute', 'error', err instanceof Error ? err.message : 'Unknown error')
            setError(err instanceof Error ? err.message : 'Unknown error')
        } finally {
            setIsExecuting(false)
        }
    }

    const copyScript = () => {
        navigator.clipboard.writeText(generatedScript)
    }

    const downloadScript = () => {
        const blob = new Blob([generatedScript], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'generated_blender_script.py'
        a.click()
        URL.revokeObjectURL(url)
    }

    return (
        <div className="p-6 max-w-6xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
                    <Wand2 className="w-6 h-6 text-purple-400" />
                    Construct
                </h1>
                <p className="text-muted-foreground">
                    Describe what you want to create. The AI will generate a Blender script and execute it.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
                {/* Left Column - Input & Steps */}
                <div className="flex flex-col gap-4">
                    {/* Prompt Input */}
                    <div className="bg-card border border-border rounded-lg p-4">
                        <label className="text-sm font-medium mb-2 block">What do you want to create?</label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="e.g., Make a dodecahedron with metal surface, 2 meters in diameter, positioned at origin..."
                            className="w-full h-24 bg-background border border-input rounded-md px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                        <div className="flex items-center justify-between mt-3">
                            <div className="flex gap-2">
                                {['dodecahedron', 'sphere', 'chair', 'robot'].map(suggestion => (
                                    <button
                                        key={suggestion}
                                        onClick={() => setPrompt(`Make a ${suggestion}`)}
                                        className="text-xs px-2 py-1 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80 transition-colors"
                                    >
                                        {suggestion}
                                    </button>
                                ))}
                            </div>
                            <button
                                onClick={generateScript}
                                disabled={!prompt.trim() || isGenerating}
                                className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
                            >
                                <Wand2 className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
                                {isGenerating ? 'Generating...' : 'Generate Script'}
                            </button>
                        </div>
                    </div>

                    {/* Progress Steps */}
                    <div className="bg-card border border-border rounded-lg p-4 flex-1">
                        <h3 className="font-medium mb-4">Progress</h3>
                        <div className="space-y-3">
                            {steps.map((step, index) => (
                                <div key={step.id} className="flex items-center gap-3">
                                    <div className={`
                                        w-6 h-6 rounded-full flex items-center justify-center text-xs
                                        ${step.status === 'completed' ? 'bg-green-500 text-white' :
                                          step.status === 'error' ? 'bg-red-500 text-white' :
                                          step.status === 'running' ? 'bg-blue-500 text-white animate-pulse' :
                                          'bg-muted text-muted-foreground'}
                                    `}>
                                        {step.status === 'completed' ? <CheckCircle className="w-4 h-4" /> :
                                         step.status === 'error' ? <AlertCircle className="w-4 h-4" /> :
                                         index + 1}
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-sm font-medium">{step.label}</div>
                                        {step.message && (
                                            <div className="text-xs text-muted-foreground">{step.message}</div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {generatedScript && (
                            <button
                                onClick={runScript}
                                disabled={isExecuting}
                                className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
                            >
                                <Play className={`w-4 h-4 ${isExecuting ? 'animate-pulse' : ''}`} />
                                {isExecuting ? 'Executing...' : 'Execute in Blender'}
                            </button>
                        )}

                        {result && (
                            <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded text-sm text-green-700">
                                {result}
                            </div>
                        )}

                        {error && (
                            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-700">
                                {error}
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column - Generated Script */}
                <div className="bg-card border border-border rounded-lg flex flex-col overflow-hidden">
                    <div className="p-3 border-b border-border bg-muted/30 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Code className="w-4 h-4 text-muted-foreground" />
                            <span className="font-medium text-sm">Generated Python Script</span>
                        </div>
                        {generatedScript && (
                            <div className="flex gap-2">
                                <button
                                    onClick={copyScript}
                                    className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"
                                    title="Copy to clipboard"
                                >
                                    <Copy className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={downloadScript}
                                    className="p-1.5 text-muted-foreground hover:text-foreground transition-colors"
                                    title="Download"
                                >
                                    <Download className="w-4 h-4" />
                                </button>
                            </div>
                        )}
                    </div>
                    <div className="flex-1 bg-[#1e1e1e] p-4 overflow-auto">
                        {generatedScript ? (
                            <pre className="font-mono text-sm text-[#d4d4d4] whitespace-pre-wrap">
                                {generatedScript}
                            </pre>
                        ) : (
                            <div className="h-full flex items-center justify-center text-muted-foreground">
                                <div className="text-center">
                                    <Code className="w-12 h-12 mx-auto mb-3 opacity-30" />
                                    <p>Your generated Blender script will appear here</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

