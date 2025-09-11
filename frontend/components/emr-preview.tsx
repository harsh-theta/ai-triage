import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
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
      <Card className="h-[600px]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            EMR Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          {summary ? (
            <div className="space-y-2">
              <h3 className="font-semibold">Live Summary</h3>
              <pre className="text-sm bg-gray-50 p-3 rounded max-h-[480px] overflow-auto whitespace-pre-wrap">{summary}</pre>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">EMR data will appear here as the triage progresses</p>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="h-[600px]">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          EMR Preview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Live Summary */}
        {summary && (
          <div>
            <h3 className="font-semibold mb-2">Live Summary</h3>
            <div className="text-sm bg-gray-50 p-3 rounded max-h-48 overflow-auto whitespace-pre-wrap font-sans">{summary}</div>
          </div>
        )}

        {/* Patient Info */}
        {data.patient_info && (
          <div>
            <h3 className="font-semibold flex items-center gap-2 mb-2">
              <User className="h-4 w-4" />
              Patient Information
            </h3>
            <div className="space-y-1 text-sm">
              {data.patient_info.age && (
                <p>
                  <span className="font-medium">Age:</span> {data.patient_info.age}
                </p>
              )}
              {data.patient_info.gender && (
                <p>
                  <span className="font-medium">Gender:</span> {data.patient_info.gender}
                </p>
              )}
              {data.patient_info.chief_complaint && (
                <p>
                  <span className="font-medium">Chief Complaint:</span> {data.patient_info.chief_complaint}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Vital Signs (optional) */}
        {data.vital_signs && (
          <div>
            <h3 className="font-semibold flex items-center gap-2 mb-2">
              <Activity className="h-4 w-4" />
              Vital Signs
            </h3>
            <div className="space-y-1 text-sm">
              {data.vital_signs.temperature && (
                <p>
                  <span className="font-medium">Temperature:</span> {data.vital_signs.temperature}
                </p>
              )}
              {data.vital_signs.blood_pressure && (
                <p>
                  <span className="font-medium">Blood Pressure:</span> {data.vital_signs.blood_pressure}
                </p>
              )}
              {data.vital_signs.heart_rate && (
                <p>
                  <span className="font-medium">Heart Rate:</span> {data.vital_signs.heart_rate}
                </p>
              )}
              {data.vital_signs.respiratory_rate && (
                <p>
                  <span className="font-medium">Respiratory Rate:</span> {data.vital_signs.respiratory_rate}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Removed Assessment and Triage Level per requirements */}

        {/* Protocol */}
        {data.protocol_followed && (
          <div>
            <h3 className="font-semibold mb-2">Protocol Followed</h3>
            <p className="text-sm bg-gray-50 p-2 rounded">{data.protocol_followed}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
