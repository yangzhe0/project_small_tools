import { FileText, Scissors, Binary, Database, Search, Cpu, MessageSquare } from 'lucide-react';

export enum PipelineStep {
  PREPARATION = 0,
  CHUNKING = 1,
  EMBEDDING = 2,
  STORAGE = 3,
  QUERY = 4,
  RETRIEVAL = 5,
  GENERATION = 6,
}

export interface StepInfo {
  id: PipelineStep;
  title: string;
  description: string;
  icon: any;
  color: string;
}

export const PIPELINE_STEPS: StepInfo[] = [
  {
    id: PipelineStep.PREPARATION,
    title: "1. 数据准备 (Data Preparation)",
    description: "收集你的本地文件（PDF, Markdown, TXT）。这是知识库的原材料。",
    icon: FileText,
    color: "text-blue-400",
  },
  {
    id: PipelineStep.CHUNKING,
    title: "2. 文本切片 (Text Chunking)",
    description: "将长文档切分成小的、语义完整的片段，以便模型处理。",
    icon: Scissors,
    color: "text-yellow-400",
  },
  {
    id: PipelineStep.EMBEDDING,
    title: "3. 向量化 (Embedding)",
    description: "使用 Embedding 模型将文本片段转化为数值向量（一串数字）。这让计算机能理解语义相似度。",
    icon: Binary,
    color: "text-green-400",
  },
  {
    id: PipelineStep.STORAGE,
    title: "4. 向量存储 (Vector Store)",
    description: "将向量和对应的文本存入本地向量数据库（如 ChromaDB, FAISS）。",
    icon: Database,
    color: "text-purple-400",
  },
  {
    id: PipelineStep.QUERY,
    title: "5. 用户提问 (User Query)",
    description: "用户提出问题，系统将问题也转化为向量。",
    icon: Search,
    color: "text-pink-400",
  },
  {
    id: PipelineStep.RETRIEVAL,
    title: "6. 语义检索 (Retrieval)",
    description: "在数据库中查找与问题向量最接近的片段（相关知识）。",
    icon: Database, // Reusing DB icon but conceptually different action
    color: "text-indigo-400",
  },
  {
    id: PipelineStep.GENERATION,
    title: "7. 生成回答 (Generation)",
    description: "将检索到的知识 + 用户问题发送给 LLM（大模型），生成最终答案。",
    icon: Cpu,
    color: "text-orange-400",
  },
];

// Mock data to start with before API call
export const INITIAL_DEMO_DATA = {
  sourceText: "React 是一个用于构建用户界面的 JavaScript 库。它由 Facebook 维护。React 使用组件化的方式开发。",
  chunks: [
    "React 是一个用于构建用户界面的 JavaScript 库。",
    "它由 Facebook 维护。",
    "React 使用组件化的方式开发。"
  ],
  vectors: [
    "[0.12, 0.45, ...]",
    "[0.88, 0.12, ...]",
    "[0.33, 0.99, ...]"
  ],
  query: "React 是谁维护的？",
  retrievedContext: "它由 Facebook 维护。",
  finalAnswer: "React 是由 Facebook 维护的。"
};