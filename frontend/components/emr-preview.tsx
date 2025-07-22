import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { EmrData } from "@/app/page"
import { User, Activity, FileText, AlertTriangle } from "lucide-react"

interface EmrPreviewProps {
  data: EmrData
}

export function EmrPreview({ data }: EmrPreviewProps) {
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
          <p className="text-gray-500 text-center py-8">EMR data will appear here as the triage progresses</p>
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

        {/* Symptoms */}
        {data.symptoms && data.symptoms.length > 0 && (
          <div>
            <h3 className="font-semibold mb-2">Symptoms</h3>
            <div className="flex flex-wrap gap-1">
              {data.symptoms.map((symptom, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {symptom}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Vital Signs */}
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

        {/* Assessment */}
        {data.assessment && (
          <div>
            <h3 className="font-semibold flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4" />
              Assessment
            </h3>
            <div className="space-y-2 text-sm">
              {data.assessment.severity && (
                <div>
                  <span className="font-medium">Severity:</span>
                  <Badge
                    className="ml-2"
                    variant={
                      data.assessment.severity === "High"
                        ? "destructive"
                        : data.assessment.severity === "Medium"
                          ? "default"
                          : "secondary"
                    }
                  >
                    {data.assessment.severity}
                  </Badge>
                </div>
              )}
              {data.assessment.recommendations && data.assessment.recommendations.length > 0 && (
                <div>
                  <p className="font-medium">Recommendations:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1">
                    {data.assessment.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
              {data.assessment.next_steps && data.assessment.next_steps.length > 0 && (
                <div>
                  <p className="font-medium">Next Steps:</p>
                  <ul className="list-disc list-inside ml-2 space-y-1">
                    {data.assessment.next_steps.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Triage Level */}
        {data.triage_level && (
          <div>
            <h3 className="font-semibold mb-2">Triage Level</h3>
            <Badge
              className="text-lg px-3 py-1"
              variant={data.triage_level <= 2 ? "destructive" : data.triage_level <= 3 ? "default" : "secondary"}
            >
              Level {data.triage_level}
            </Badge>
          </div>
        )}

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
