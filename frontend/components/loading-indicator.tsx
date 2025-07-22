import { Loader2 } from "lucide-react"

export function LoadingIndicator() {
  return (
    <div className="flex items-center justify-center p-4 border-t bg-gray-50">
      <div className="flex items-center gap-2 text-gray-600">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm">AI is analyzing your symptoms...</span>
      </div>
    </div>
  )
}
