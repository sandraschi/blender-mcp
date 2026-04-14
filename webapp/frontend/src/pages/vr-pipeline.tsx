import { AlertTriangle, ArrowRight, CheckCircle, Glasses } from "lucide-react";
import { useState } from "react";

export default function VRPipeline() {
  const [activeStep, setActiveStep] = useState(1);
  const [platform, setPlatform] = useState<"unity" | "vrchat" | "resonite">("unity");

  const steps = [
    { id: 1, name: "Optimization", status: "completed" },
    { id: 2, name: "Rigging Check", status: "current" },
    { id: 3, name: "Material Bake", status: "pending" },
    { id: 4, name: "Export", status: "pending" },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
          <Glasses className="w-6 h-6 text-indigo-400" />
          VR Pipeline
        </h1>
        <p className="text-muted-foreground">Prepare and export assets for VR platforms.</p>
      </div>

      {/* Platform Selector */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { id: "unity", label: "Unity / VRChat", icon: "Unity" },
          { id: "unreal", label: "Unreal Engine", icon: "UE" },
          { id: "resonite", label: "Resonite", icon: "Res" },
        ].map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => setPlatform(p.id as "unity" | "vrchat" | "resonite")}
            className={`p-4 rounded-lg border text-left transition-all ${
              platform === p.id
                ? "bg-primary text-primary-foreground border-primary ring-2 ring-primary/20"
                : "bg-card border-border hover:bg-accent hover:text-accent-foreground"
            }`}
          >
            <div className="font-bold mb-1">{p.label}</div>
            <div className="text-xs opacity-80">Target Platform</div>
          </button>
        ))}
      </div>

      {/* Progress */}
      <div className="mb-8 relative">
        <div className="absolute top-1/2 left-0 w-full h-1 bg-muted -translate-y-1/2 z-0" />
        <div className="flex justify-between relative z-10">
          {steps.map((step) => (
            <div key={step.id} className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                  step.id < activeStep
                    ? "bg-green-500 border-green-500 text-white"
                    : step.id === activeStep
                      ? "bg-background border-primary text-primary"
                      : "bg-background border-muted text-muted-foreground"
                }`}
              >
                {step.id < activeStep ? <CheckCircle className="w-6 h-6" /> : step.id}
              </div>
              <span
                className={`mt-2 text-xs font-medium ${step.id === activeStep ? "text-primary" : "text-muted-foreground"}`}
              >
                {step.name}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Content */}
      <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Step 2: Rigging Validation</h2>
          <span className="px-3 py-1 bg-yellow-500/10 text-yellow-500 rounded-full text-xs font-medium border border-yellow-500/20 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            Warnings Found
          </span>
        </div>

        <div className="space-y-4 mb-6">
          <div className="p-4 bg-muted/30 rounded-lg flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            <div>
              <h4 className="font-medium">Bone Hierarchy</h4>
              <p className="text-sm text-muted-foreground">
                Armature structure matches Unity Humanoid standards.
              </p>
            </div>
          </div>

          <div className="p-4 bg-yellow-500/5 border border-yellow-500/20 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5" />
            <div>
              <h4 className="font-medium text-yellow-500">Weight Painting Issues</h4>
              <p className="text-sm text-yellow-600/80">
                3 vertices found with zero weights in 'LeftHand'.
              </p>
              <button
                type="button"
                className="mt-2 text-xs bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-500 px-3 py-1.5 rounded transition-colors"
              >
                Auto-Fix Weights
              </button>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="button"
            className="px-4 py-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            Previous
          </button>
          <button
            type="button"
            onClick={() => setActiveStep(Math.min(steps.length + 1, activeStep + 1))}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            Continue <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
