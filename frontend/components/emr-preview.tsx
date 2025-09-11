import { Badge } from "@/components/ui/badge"
import type { EmrData } from "@/app/page"
import { User, Activity, FileText, AlertTriangle } from "lucide-react"

interface EmrPreviewProps {
  data: EmrData
  summary?: string
}

export function EmrPreview({ data, summary }: EmrPreviewProps) {
  const isEmpty = Object.keys(data).length === 0

  if (isEmpty) {
    return (
      <div className="px-6 py-4">
        {summary ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-2 h-2 bg-[hsl(var(--theta-teal))] rounded-full animate-pulse"></div>
              <h3 className="font-semibold text-gray-900">Live Assessment</h3>
            </div>
            <div className="bg-gray-50 p-4 border-l-4 border-[hsl(var(--theta-teal))]">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">{summary}</pre>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">EMR data will appear here</p>
            <p className="text-gray-400 text-sm">as the triage assessment progresses</p>
          </div>
        )}
        <div className="pb-4"></div>
      </div>
    )
  }

  return (
    <div className="px-6 py-4 space-y-6 pb-8">
      {/* Live Summary */}
      {summary && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 bg-[hsl(var(--theta-teal))] rounded-full animate-pulse"></div>
            <h3 className="font-semibold text-gray-900">Live Assessment</h3>
          </div>
          <div className="bg-gradient-to-r from-[hsl(var(--theta-teal))]/5 to-[hsl(var(--theta-cyan))]/5 p-4 border-l-4 border-[hsl(var(--theta-teal))]">
            <div className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">{summary}</div>
          </div>
        </div>
      )}

      {/* Patient Info */}
      {data.patient_info && (
        <div>
          <h3 className="font-semibold flex items-center gap-2 mb-3 text-gray-900">
            <User className="h-5 w-5 text-[hsl(var(--theta-teal))]" />
            Patient Information
          </h3>
          <div className="bg-gray-50 p-4 space-y-3">
            {data.patient_info.age && (
              <div className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span className="text-gray-600">Age</span>
                <span className="font-medium text-gray-900">{data.patient_info.age}</span>
              </div>
            )}
            {data.patient_info.gender && (
              <div className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span className="text-gray-600">Gender</span>
                <span className="font-medium text-gray-900">{data.patient_info.gender}</span>
              </div>
            )}
            {data.patient_info.chief_complaint && (
              <div className="py-2">
                <span className="text-gray-600 block mb-1">Chief Complaint</span>
                <span className="font-medium text-gray-900">{data.patient_info.chief_complaint}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Vital Signs */}
      {data.vital_signs && (
        <div>
          <h3 className="font-semibold flex items-center gap-2 mb-3 text-gray-900">
            <Activity className="h-5 w-5 text-[hsl(var(--theta-teal))]" />
            Vital Signs
          </h3>
          <div className="bg-gray-50 p-4 space-y-3">
            {data.vital_signs.temperature && (
              <div className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span className="text-gray-600">Temperature</span>
                <span className="font-medium text-gray-900">{data.vital_signs.temperature}</span>
              </div>
            )}
            {data.vital_signs.blood_pressure && (
              <div className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span className="text-gray-600">Blood Pressure</span>
                <span className="font-medium text-gray-900">{data.vital_signs.blood_pressure}</span>
              </div>
            )}
            {data.vital_signs.heart_rate && (
              <div className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span className="text-gray-600">Heart Rate</span>
                <span className="font-medium text-gray-900">{data.vital_signs.heart_rate}</span>
              </div>
            )}
            {data.vital_signs.respiratory_rate && (
              <div className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span className="text-gray-600">Respiratory Rate</span>
                <span className="font-medium text-gray-900">{data.vital_signs.respiratory_rate}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Protocol */}
      {data.protocol_followed && (
        <div>
          <h3 className="font-semibold mb-3 text-gray-900">Protocol Followed</h3>
          <div className="bg-blue-50 p-4 border-l-4 border-blue-400">
            <p className="text-sm text-blue-800">{data.protocol_followed}</p>
          </div>
        </div>
      )}
    </div>
  )
}
