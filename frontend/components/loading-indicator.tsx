import { Loader2 } from "lucide-react"

export function LoadingIndicator() {
  return (
    <div className="flex items-center justify-center p-6 border-t bg-gradient-to-r from-[hsl(var(--theta-teal))]/5 to-[hsl(var(--theta-cyan))]/5">
      <div className="flex items-center gap-3">
        <div className="relative">
          <Loader2 className="h-6 w-6 animate-spin text-[hsl(var(--theta-teal))]" />
          <div className="absolute inset-0 h-6 w-6 animate-ping rounded-full bg-[hsl(var(--theta-teal))]/20"></div>
        </div>
        <span className="text-base font-medium text-gray-700">AI is analyzing your symptoms...</span>
      </div>
    </div>
  )
}
