import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export async function transpileCurlToPython(curl: string): Promise<{ python: string; method?: string; endpoint?: string; format?: string }> {
  const prompt = `
    You are a professional software engineer. 
    Convert the following cURL command into a clean, modern Python script using the 'requests' library.
    Return ONLY a JSON object with the following fields:
    - python: The complete python code.
    - method: The HTTP method (e.g., POST, GET).
    - endpoint: The hostname or base path.
    - format: The data format (e.g., JSON, FORM, MULTIPART).

    cURL Command:
    ${curl}
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json"
      }
    });
    
    const responseText = response.text || "";
    
    // Attempt to parse JSON from the response
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    
    return { python: responseText };
  } catch (error) {
    console.error("Transpilation failed:", error);
    throw error;
  }
}
