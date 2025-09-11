import { Badge } from "@/components/ui/badge"
import { Activity, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

interface SystemStatusProps {
  protocol: string
  status: "active" | "emergency_detected" | "error" | "complete"
}

export function SystemStatus({ protocol, status }: SystemStatusProps) {
  const getStatusConfig = () => {
    switch (status) {
      case "active":
        return {
          icon: Activity,
          label: "Active Assessment",
          variant: "default" as const,
          color: "text-white",
          bgColor: "bg-white/20",
        }
      case "emergency_detected":
        return {
          icon: AlertTriangle,
          label: "Emergency Detected",
          variant: "destructive" as const,
          color: "text-white",
          bgColor: "bg-red-500/90",
        }
      case "error":
        return {
          icon: XCircle,
          label: "System Error",
          variant: "destructive" as const,
          color: "text-white",
          bgColor: "bg-red-500/90",
        }
      case "complete":
        return {
          icon: CheckCircle,
          label: "Assessment Complete",
          variant: "secondary" as const,
          color: "text-white",
          bgColor: "bg-green-500/90",
        }
      default:
        return {
          icon: Activity,
          label: "Unknown Status",
          variant: "secondary" as const,
          color: "text-white",
          bgColor: "bg-gray-500/90",
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <div className="flex items-center justify-between text-white">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Icon className="h-5 w-5 text-white" />
          <span className="font-semibold text-lg">AI Triage System</span>
        </div>
        <div className="hidden md:block text-white/90">
          Current Protocol: <span className="font-medium">{protocol}</span>
        </div>
      </div>
      <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${config.bgColor} backdrop-blur-sm`}>
        <Icon className="h-4 w-4" />
        <span className="font-medium text-sm">{config.label}</span>
      </div>
    </div>
  )
}
