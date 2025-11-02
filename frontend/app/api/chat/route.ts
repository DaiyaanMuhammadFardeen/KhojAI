import { generateText } from "ai"

export async function POST(request: Request) {
  try {
    const { message } = await request.json()

    if (!message || typeof message !== "string") {
      return Response.json({ error: "Invalid message" }, { status: 400 })
    }

    const { text } = await generateText({
      model: "openai/gpt-4-mini",
      prompt: message,
      system: "You are a helpful AI assistant. Provide clear, concise, and accurate responses.",
    })

    return Response.json({ response: text })
  } catch (error) {
    console.error("Chat API error:", error)
    return Response.json({ error: "Failed to generate response" }, { status: 500 })
  }
}
