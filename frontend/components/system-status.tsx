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
          label: "Active",
          variant: "default" as const,
          color: "text-blue-600",
        }
      case "emergency_detected":
        return {
          icon: AlertTriangle,
          label: "Emergency Detected",
          variant: "destructive" as const,
          color: "text-red-600",
        }
      case "error":
        return {
          icon: XCircle,
          label: "Error",
          variant: "destructive" as const,
          color: "text-red-600",
        }
      case "complete":
        return {
          icon: CheckCircle,
          label: "Complete",
          variant: "secondary" as const,
          color: "text-green-600",
        }
      default:
        return {
          icon: Activity,
          label: "Unknown",
          variant: "secondary" as const,
          color: "text-gray-600",
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Icon className={`h-4 w-4 ${config.color}`} />
        <span className="font-medium">Protocol:</span>
        <span className="text-sm">{protocol}</span>
      </div>
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    </div>
  )
}
