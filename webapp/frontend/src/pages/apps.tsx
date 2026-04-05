import { Activity, Zap } from "lucide-react";
import { FLEET_REGISTRY } from '../common/apps-catalog';
import { FleetCard } from '../common/FleetCard';

export default function Apps() {
    return (
        <div className="space-y-6 p-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Fleet Navigation</h2>
                    <p className="text-muted-foreground">Connect to other SOTA standard applications with one-click orchestration.</p>
                </div>
                <div className="flex items-center gap-2 rounded-md bg-muted/50 px-3 py-1 text-xs text-muted-foreground border border-border">
                    <Activity className="h-3 w-3 text-emerald-500" />
                    Fleet Sync Active
                </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {FLEET_REGISTRY.map((member) => (
                    <FleetCard
                        key={member.id}
                        member={member}
                        currentAppId="blender-mcp"
                    />
                ))}

                <div className="h-full border-dashed border-border bg-transparent hover:border-muted-foreground/20 border rounded-xl transition-colors flex flex-col items-center justify-center p-6 text-center group">
                    <Zap className="h-10 w-10 text-muted group-hover:text-primary/20 transition-colors mb-4" />
                    <p className="text-xs text-muted-foreground group-hover:text-muted transition-colors">
                        More apps arriving soon...
                    </p>
                </div>
            </div>
        </div>
    );
}
