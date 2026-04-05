import { useState } from 'react'
import { Grid, List, Search, Download, Filter } from 'lucide-react'

const MOCK_MATERIALS = [
    { id: 1, name: "Polished Concrete", category: "Concrete", color: "#808080" },
    { id: 2, name: "Gold Leaf", category: "Metal", color: "#FFD700" },
    { id: 3, name: "Mahogany Wood", category: "Wood", color: "#4A0404" },
    { id: 4, name: "Blue Glass", category: "Glass", color: "#87CEEB", opacity: 0.5 },
    { id: 5, name: "Red Plastic", category: "Plastic", color: "#FF0000" },
    { id: 6, name: "Brushed Steel", category: "Metal", color: "#C0C0C0" },
    { id: 7, name: "Marble White", category: "Stone", color: "#F5F5F5" },
    { id: 8, name: "Leather Black", category: "Fabric", color: "#1A1A1A" },
]

export default function MaterialStore() {
    const [view, setView] = useState<'grid' | 'list'>('grid')
    const [search, setSearch] = useState('')

    const filteredMaterials = MOCK_MATERIALS.filter(m =>
        m.name.toLowerCase().includes(search.toLowerCase()) ||
        m.category.toLowerCase().includes(search.toLowerCase())
    )

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight mb-1">Material Store</h1>
                    <p className="text-muted-foreground">Browse and apply materials to selected objects.</p>
                </div>

                <div className="flex items-center space-x-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Search materials..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-9 pr-4 py-2 bg-background border border-input rounded-md w-64 focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                    </div>

                    <div className="flex items-center border border-border rounded-md bg-card">
                        <button
                            onClick={() => setView('grid')}
                            className={`p-2 ${view === 'grid' ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                        >
                            <Grid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setView('list')}
                            className={`p-2 ${view === 'list' ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            <div className="flex gap-6">
                {/* Sidebar Filters */}
                <div className="w-64 hidden lg:block space-y-6">
                    <div>
                        <h3 className="font-semibold mb-3 flex items-center gap-2">
                            <Filter className="w-4 h-4" /> Categories
                        </h3>
                        <div className="space-y-1">
                            {['All', 'Concrete', 'Metal', 'Wood', 'Glass', 'Plastic', 'Stone', 'Fabric'].map(cat => (
                                <button key={cat} className="w-full text-left px-2 py-1.5 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground rounded transition-colors">
                                    {cat}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* content */}
                <div className="flex-1">
                    {view === 'grid' ? (
                        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
                            {filteredMaterials.map(material => (
                                <div key={material.id} className="group border border-border rounded-lg bg-card overflow-hidden hover:ring-2 hover:ring-primary transition-all cursor-pointer">
                                    <div className="aspect-square bg-muted relative flex items-center justify-center">
                                        <div
                                            className="w-24 h-24 rounded-full shadow-xl"
                                            style={{
                                                backgroundColor: material.color,
                                                opacity: material.opacity || 1
                                            }}
                                        />
                                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                                            <button className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 transform translate-y-4 group-hover:translate-y-0 transition-all">
                                                <Download className="w-4 h-4" /> Apply
                                            </button>
                                        </div>
                                    </div>
                                    <div className="p-3">
                                        <h3 className="font-medium truncate">{material.name}</h3>
                                        <p className="text-xs text-muted-foreground">{material.category}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {filteredMaterials.map(material => (
                                <div key={material.id} className="flex items-center p-3 border border-border rounded-lg bg-card hover:bg-accent/50 transition-colors group">
                                    <div
                                        className="w-10 h-10 rounded-md shadow-sm mr-4"
                                        style={{ backgroundColor: material.color }}
                                    />
                                    <div className="flex-1">
                                        <h3 className="font-medium">{material.name}</h3>
                                        <p className="text-xs text-muted-foreground">{material.category}</p>
                                    </div>
                                    <button className="opacity-0 group-hover:opacity-100 bg-primary text-primary-foreground px-3 py-1.5 rounded text-sm font-medium transition-opacity">
                                        Apply
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
