import React, { useState, useEffect } from 'react';
import { PipelineStep, PIPELINE_STEPS, INITIAL_DEMO_DATA } from './constants';
import StepVisualizer from './components/StepVisualizer';
import { generateDemoData, GeneratedDemoData } from './services/geminiService';
import { ChevronRight, ChevronLeft, RefreshCw, Wand2, Info, CheckCircle2 } from 'lucide-react';
import clsx from 'clsx';

const App: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<PipelineStep>(PipelineStep.PREPARATION);
  const [demoTopic, setDemoTopic] = useState<string>("");
  const [demoData, setDemoData] = useState<GeneratedDemoData>(INITIAL_DEMO_DATA);
  const [isLoading, setIsLoading] = useState(false);
  const [isApiKeySet, setIsApiKeySet] = useState(true); // Assuming env var is present for simplicity in this demo structure, realistically would check.

  const currentStepInfo = PIPELINE_STEPS[currentStep];

  const handleNext = () => {
    if (currentStep < PipelineStep.GENERATION) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > PipelineStep.PREPARATION) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleGenerateScenario = async () => {
    if (!demoTopic.trim()) return;
    setIsLoading(true);
    try {
      const newData = await generateDemoData(demoTopic);
      setDemoData(newData);
      setCurrentStep(PipelineStep.PREPARATION); // Reset to start
    } catch (error) {
      console.error("Failed to generate", error);
      alert("无法生成示例，请检查 API Key 配置或稍后再试。");
    } finally {
      setIsLoading(false);
    }
  };

  // Pre-fetch check (simulated)
  useEffect(() => {
    // Ideally check process.env.API_KEY here if needed
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center py-10 px-4">
      
      {/* Header */}
      <header className="mb-10 text-center max-w-2xl">
        <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400 mb-4">
          Local RAG Visualizer
        </h1>
        <p className="text-slate-400 text-lg">
          十分钟学会：如何搭建你的本地知识库 (Retrieval Augmented Generation)
        </p>
      </header>

      {/* Main Content Area */}
      <main className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Controls & Context */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Progress List */}
          <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700 shadow-xl">
            <h2 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
              <Info className="w-5 h-5 text-blue-400" />
              流程步骤
            </h2>
            <div className="space-y-4 relative">
               {/* Connector Line */}
               <div className="absolute left-[19px] top-2 bottom-2 w-0.5 bg-slate-700 z-0"></div>
               
               {PIPELINE_STEPS.map((step) => {
                 const isActive = currentStep === step.id;
                 const isCompleted = currentStep > step.id;
                 const Icon = step.icon;

                 return (
                   <button
                     key={step.id}
                     onClick={() => setCurrentStep(step.id)}
                     className={clsx(
                       "relative z-10 w-full flex items-center gap-3 p-2 rounded-lg transition-all text-left",
                       isActive ? "bg-slate-700/50 translate-x-1" : "hover:bg-slate-700/30"
                     )}
                   >
                     <div className={clsx(
                       "w-10 h-10 rounded-full flex items-center justify-center border-2 shrink-0 transition-colors",
                       isActive ? `${step.color} border-current bg-slate-900` : 
                       isCompleted ? "bg-emerald-500/20 border-emerald-500 text-emerald-500" :
                       "border-slate-600 text-slate-600 bg-slate-900"
                     )}>
                       {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
                     </div>
                     <div className="flex flex-col">
                       <span className={clsx("font-medium text-sm", isActive ? "text-white" : "text-slate-400")}>
                         {step.title}
                       </span>
                     </div>
                   </button>
                 );
               })}
            </div>
          </div>

          {/* Interactive Demo Generator */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700 shadow-xl">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Wand2 className="w-5 h-5 text-purple-400" />
              自定义演示场景
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              输入一个你感兴趣的主题（例如：烹饪、量子物理、园艺），AI 将为你生成该主题下的 RAG 演示数据。
            </p>
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="输入主题..." 
                className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                value={demoTopic}
                onChange={(e) => setDemoTopic(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGenerateScenario()}
              />
              <button 
                onClick={handleGenerateScenario}
                disabled={isLoading || !demoTopic}
                className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white p-2 rounded-lg transition-colors"
              >
                {isLoading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Wand2 className="w-5 h-5" />}
              </button>
            </div>
          </div>

        </div>

        {/* Right Column: Visualization Stage */}
        <div className="lg:col-span-2 flex flex-col gap-6">
           
           {/* The Stage */}
           <div className="bg-slate-950 p-1 rounded-3xl shadow-2xl border border-slate-800">
             <StepVisualizer currentStep={currentStep} data={demoData} />
           </div>

           {/* Explainer Card */}
           <div className="bg-slate-800 rounded-2xl p-8 border border-slate-700 flex flex-col justify-between min-h-[160px] relative overflow-hidden">
              <div className="absolute top-0 right-0 p-3 opacity-10">
                 {(() => {
                    const Icon = currentStepInfo.icon;
                    return <Icon className="w-32 h-32" />;
                 })()}
              </div>

              <div className="z-10">
                <div className="flex items-center gap-3 mb-2">
                   <h2 className={clsx("text-2xl font-bold", currentStepInfo.color)}>
                     {currentStepInfo.title.split(' ')[1]} 
                   </h2>
                   <span className="text-xs font-mono bg-slate-900 px-2 py-1 rounded text-slate-400">Step {currentStep + 1}/7</span>
                </div>
                <p className="text-slate-300 text-lg leading-relaxed">
                  {currentStepInfo.description}
                </p>
                {currentStep === PipelineStep.PREPARATION && (
                   <p className="mt-2 text-sm text-slate-500">工具推荐: Python, Unstructured.io, PDFMiner</p>
                )}
                {currentStep === PipelineStep.CHUNKING && (
                   <p className="mt-2 text-sm text-slate-500">工具推荐: LangChain TextSplitter</p>
                )}
                {currentStep === PipelineStep.EMBEDDING && (
                   <p className="mt-2 text-sm text-slate-500">模型推荐: OpenAI text-embedding-3, HuggingFace m3e-base</p>
                )}
                {currentStep === PipelineStep.STORAGE && (
                   <p className="mt-2 text-sm text-slate-500">数据库推荐: ChromaDB, Qdrant, Pgvector</p>
                )}
                {currentStep === PipelineStep.GENERATION && (
                   <p className="mt-2 text-sm text-slate-500">模型推荐: Gemini 2.5 Flash, GPT-4, Llama 3</p>
                )}
              </div>

              {/* Navigation Controls */}
              <div className="flex items-center justify-between mt-6 pt-6 border-t border-slate-700/50 z-10">
                <button
                  onClick={handlePrev}
                  disabled={currentStep === 0}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                >
                  <ChevronLeft className="w-5 h-5" />
                  上一步
                </button>

                <div className="flex gap-1">
                   {PIPELINE_STEPS.map((_, idx) => (
                      <div key={idx} className={clsx("w-2 h-2 rounded-full transition-colors", idx === currentStep ? "bg-blue-400" : "bg-slate-700")} />
                   ))}
                </div>

                <button
                  onClick={handleNext}
                  disabled={currentStep === PipelineStep.GENERATION}
                  className="flex items-center gap-2 px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium disabled:opacity-30 disabled:hover:bg-blue-600 transition-all shadow-lg shadow-blue-900/20"
                >
                  下一步
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
           </div>

        </div>

      </main>
    </div>
  );
};

export default App;