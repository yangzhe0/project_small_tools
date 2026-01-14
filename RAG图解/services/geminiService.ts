import { GoogleGenAI, Type } from "@google/genai";

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

export interface GeneratedDemoData {
  sourceText: string;
  chunks: string[];
  query: string;
  retrievedContext: string;
  finalAnswer: string;
}

export const generateDemoData = async (topic: string): Promise<GeneratedDemoData> => {
  if (!apiKey) {
    throw new Error("API Key is missing");
  }

  const model = "gemini-2.5-flash";
  const prompt = `Generate a simplified example of RAG (Retrieval Augmented Generation) data processing for the topic: "${topic}".
  
  Return a JSON object with the following fields:
  - sourceText: A short paragraph (2-3 sentences) explaining the basics of the topic.
  - chunks: An array of strings, splitting the sourceText into logical parts.
  - query: A simple question a user might ask about this topic based on the text.
  - retrievedContext: The specific chunk from the 'chunks' array that best answers the query.
  - finalAnswer: A direct answer to the query based on the retrievedContext.
  
  Language: Simplified Chinese.`;

  try {
    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            sourceText: { type: Type.STRING },
            chunks: { 
              type: Type.ARRAY,
              items: { type: Type.STRING }
            },
            query: { type: Type.STRING },
            retrievedContext: { type: Type.STRING },
            finalAnswer: { type: Type.STRING }
          },
          required: ["sourceText", "chunks", "query", "retrievedContext", "finalAnswer"]
        }
      }
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    
    return JSON.parse(text) as GeneratedDemoData;
  } catch (error) {
    console.error("Gemini generation error:", error);
    // Fallback or re-throw
    throw error;
  }
};