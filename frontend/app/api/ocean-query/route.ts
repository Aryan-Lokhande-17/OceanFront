// frontend/app/api/ocean-query/route.ts
// This route uses the Python backend for intelligent data queries
// Falls back to Groq if backend is unavailable

import { NextResponse } from "next/server"

export const runtime = 'nodejs'

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

interface QueryRequest {
  query: string
  include_sql?: boolean
}

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const userQuery = body.messages?.[0]?.content || body.query || ""

    if (!userQuery) {
      return NextResponse.json(
        { error: "No query provided" },
        { status: 400 }
      )
    }

    console.log("📝 Query received:", userQuery)
    console.log("🔗 Attempting to call Python backend at:", BACKEND_URL)

    // Step 1: Try to call Python backend for intelligent data query
    try {
      const backendResponse = await fetch(`${BACKEND_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: userQuery,
          include_sql: false,
        }),
        timeout: 30000,
      })

      if (backendResponse.ok) {
        const result = await backendResponse.json()
        
        console.log("✅ Backend query successful!")
        console.log(`📊 Rows returned: ${result.row_count}`)

        // Create readable stream from markdown response
        const encoder = new TextEncoder()
        const readableStream = new ReadableStream({
          start(controller) {
            controller.enqueue(encoder.encode(result.markdown_result || "No results"))
            controller.close()
          },
        })

        return new Response(readableStream, {
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          status: 200,
        })
      } else {
        console.warn("⚠️  Backend returned error status:", backendResponse.status)
        throw new Error(`Backend error: ${backendResponse.status}`)
      }
    } catch (backendError: any) {
      console.error("❌ Backend error, falling back to Groq:", backendError.message)

      // Step 2: Fallback to Groq chat API
      console.log("🔄 Using Groq as fallback...")
      const fallbackResponse = await fetch("http://localhost:3000/api/ocean-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: body.messages || [{ role: "user", content: userQuery }] }),
      })

      if (fallbackResponse.ok && fallbackResponse.body) {
        return new Response(fallbackResponse.body, {
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          status: 200,
        })
      } else {
        throw new Error("Both backend and fallback failed")
      }
    }
  } catch (error: any) {
    console.error("Critical Error:", error)

    const encoder = new TextEncoder()
    const readableStream = new ReadableStream({
      start(controller) {
        const message = `⚠️ Error: ${error.message}\n\n💡 Tips:\n- Ensure Python backend is running at http://localhost:8000\n- Check that GROQ_API_KEY is valid in .env files\n- Try: "Show me SST data from Chennai" or "List west coast buoys"`
        controller.enqueue(encoder.encode(message))
        controller.close()
      },
    })

    return new Response(readableStream, {
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      status: 200,
    })
  }
}
