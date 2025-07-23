import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://106.201.228.100:9001"
    const backendRes = await fetch(
      `${backendUrl}/chat`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: body.message,
          session_id: body.session_id,
          // Optionally pass conversation_history if backend supports it
        }),
      },
    )

    if (!backendRes.ok) {
      const errorData = await backendRes.json()
      return NextResponse.json(errorData, { status: backendRes.status })
    }

    const data = await backendRes.json()
    // Adapt backend response to frontend expectations
    return NextResponse.json({
      message: data.ai_message,
      status: data.status,
      current_protocol: data.protocol,
      emr_data: data.emr_data,
      messages: data.messages,
    })
  } catch (error) {
    return NextResponse.json(
      {
        message: "I'm sorry, there was an error processing your request. Please try again.",
        status: "error",
      },
      { status: 500 }
    )
  }
}
