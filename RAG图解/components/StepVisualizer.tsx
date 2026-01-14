import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PipelineStep, StepInfo, PIPELINE_STEPS } from '../constants';
import { FileText, Scissors, Binary, Database, Search, ArrowRight, Brain, MessageSquare, Sparkles } from 'lucide-react';

interface VisualizerProps {
  currentStep: PipelineStep;
  data: {
    sourceText: string;
    chunks: string[];
    vectors: string[]; // Just strings representing vectors like "[0.1, ...]"
    query: string;
    retrievedContext: string;
    finalAnswer: string;
  };
}

const StepVisualizer: React.FC<VisualizerProps> = ({ currentStep, data }) => {
  
  // Animation Variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.5 } },
    exit: { opacity: 0, transition: { duration: 0.3 } }
  };

  const itemVariants = {
    hidden: { scale: 0, opacity: 0, y: 20 },
    visible: (i: number) => ({
      scale: 1,
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.1, type: "spring", stiffness: 100 }
    }),
    exit: { scale: 0, opacity: 0 }
  };

  const flowLineVariants = {
    hidden: { pathLength: 0, opacity: 0 },
    visible: { pathLength: 1, opacity: 1, transition: { duration: 1.5, ease: "easeInOut" } }
  };

  return (
    <div className="relative w-full h-[400px] md:h-[500px] bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden flex items-center justify-center p-4 shadow-inner">
      
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ backgroundImage: 'radial-gradient(#94a3b8 1px, transparent 1px)', backgroundSize: '24px 24px' }}>
      </div>

      <AnimatePresence mode="wait">
        
        {/* Step 1: Preparation */}
        {currentStep === PipelineStep.PREPARATION && (
          <motion.div 
            key="prep"
            variants={containerVariants}
            initial="hidden" animate="visible" exit="exit"
            className="flex flex-col items-center gap-4"
          >
            <motion.div 
              className="w-24 h-32 bg-blue-500/20 border-2 border-blue-400 rounded-lg flex items-center justify-center relative"
              initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ repeat: Infinity, repeatType: "reverse", duration: 2 }}
            >
              <FileText className="w-12 h-12 text-blue-400" />
              <div className="absolute -top-2 -right-2 bg-blue-600 text-xs px-2 py-1 rounded-full text-white">DOC</div>
            </motion.div>
            <div className="bg-slate-700/80 p-3 rounded-lg max-w-sm text-sm text-slate-200 border border-slate-600">
              <p className="font-mono text-xs text-blue-300 mb-1">source.txt</p>
              "{data.sourceText}"
            </div>
          </motion.div>
        )}

        {/* Step 2: Chunking */}
        {currentStep === PipelineStep.CHUNKING && (
          <motion.div 
            key="chunk"
            variants={containerVariants}
            initial="hidden" animate="visible" exit="exit"
            className="flex items-center gap-8"
          >
             <div className="opacity-30 scale-75">
                <FileText className="w-16 h-16 text-slate-500" />
             </div>
             <ArrowRight className="text-slate-500 w-6 h-6 animate-pulse" />
             <div className="grid grid-cols-1 gap-2">
                {data.chunks.map((chunk, idx) => (
                  <motion.div 
                    key={idx}
                    custom={idx}
                    variants={itemVariants}
                    className="flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/30 p-2 rounded max-w-[200px]"
                  >
                    <Scissors className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                    <span className="text-xs text-yellow-200 truncate">{chunk}</span>
                  </motion.div>
                ))}
             </div>
          </motion.div>
        )}

        {/* Step 3: Embedding */}
        {currentStep === PipelineStep.EMBEDDING && (
          <motion.div 
            key="embed"
            variants={containerVariants}
            initial="hidden" animate="visible" exit="exit"
            className="flex items-center gap-6"
          >
             <div className="flex flex-col gap-2 opacity-50">
               {[1,2,3].map(i => <div key={i} className="w-16 h-4 bg-yellow-500/20 rounded"></div>)}
             </div>
             <ArrowRight className="text-slate-500 w-6 h-6 animate-pulse" />
             <div className="grid grid-cols-1 gap-4">
                {data.chunks.map((_, idx) => (
                  <motion.div 
                    key={idx}
                    custom={idx}
                    variants={itemVariants}
                    className="flex items-center gap-3"
                  >
                    <div className="w-24 h-6 bg-green-500/10 border border-green-500/30 rounded flex items-center justify-center overflow-hidden relative">
                       <span className="text-[10px] font-mono text-green-400 tracking-tighter">
                         [0.12, 0.95, 0.33...]
                       </span>
                       <motion.div 
                          className="absolute inset-0 bg-green-400/20"
                          initial={{ x: '-100%' }}
                          animate={{ x: '100%' }}
                          transition={{ repeat: Infinity, duration: 1.5, delay: idx * 0.2 }}
                       />
                    </div>
                    <Binary className="w-4 h-4 text-green-500" />
                  </motion.div>
                ))}
             </div>
          </motion.div>
        )}

        {/* Step 4: Storage */}
        {currentStep === PipelineStep.STORAGE && (
          <motion.div 
            key="storage"
            variants={containerVariants}
            initial="hidden" animate="visible" exit="exit"
            className="flex flex-col items-center justify-center"
          >
            <motion.div 
              className="relative w-32 h-40"
            >
              <Database className="w-32 h-32 text-purple-500 absolute bottom-0 z-10" />
              <motion.div
                 className="absolute top-0 left-1/2 -translate-x-1/2 flex flex-col gap-2 z-0"
                 initial={{ y: -50, opacity: 0 }}
                 animate={{ y: 20, opacity: 1 }}
                 transition={{ duration: 1, staggerChildren: 0.2 }}
              >
                  {[1,2,3].map(i => (
                    <motion.div 
                      key={i}
                      initial={{ y: -50, opacity: 0, scale: 0.5 }}
                      animate={{ y: 40, opacity: 0, scale: 0.2 }} // Disappear into DB
                      transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.5 }}
                      className="w-16 h-4 bg-green-400 rounded-full blur-[2px]"
                    />
                  ))}
              </motion.div>
            </motion.div>
            <div className="mt-4 text-center">
              <h3 className="text-purple-400 font-semibold">Vector Database</h3>
              <p className="text-xs text-slate-400">Chroma / Milvus / FAISS</p>
            </div>
          </motion.div>
        )}

        {/* Step 5: Query */}
        {currentStep === PipelineStep.QUERY && (
          <motion.div 
            key="query"
            variants={containerVariants}
            initial="hidden" animate="visible" exit="exit"
            className="flex items-center gap-4"
          >
             <motion.div 
               initial={{ x: -50, opacity: 0 }}
               animate={{ x: 0, opacity: 1 }}
               className="bg-slate-700 p-4 rounded-xl border border-slate-600 rounded-bl-none"
             >
                <div className="flex items-center gap-2 mb-2">
                   <div className="w-8 h-8 rounded-full bg-slate-500 flex items-center justify-center">
                      <Search className="w-4 h-4 text-white" />
                   </div>
                   <span className="text-sm font-semibold text-slate-200">User</span>
                </div>
                <p className="text-lg text-white">"{data.query}"</p>
             </motion.div>
             
             <ArrowRight className="text-pink-500 w-8 h-8" />

             <motion.div
               initial={{ scale: 0, opacity: 0 }}
               animate={{ scale: 1, opacity: 1 }}
               transition={{ delay: 0.5 }}
               className="bg-pink-500/10 border border-pink-500 p-2 rounded font-mono text-pink-400 text-xs"
             >
               VECTOR:<br/>[0.82, -0.14...]
             </motion.div>
          </motion.div>
        )}

        {/* Step 6: Retrieval */}
        {currentStep === PipelineStep.RETRIEVAL && (
          <motion.div 
            key="retrieval"
            variants={containerVariants}
            initial="hidden" animate="visible" exit="exit"
            className="flex items-center justify-center w-full max-w-lg relative h-64"
          >
            {/* The DB */}
            <Database className="w-24 h-24 text-slate-600 absolute left-0 top-1/2 -translate-y-1/2" />
            
            {/* Query Vector entering */}
            <motion.div 
               className="absolute left-8 top-1/2 -translate-y-1/2 z-10 w-4 h-4 bg-pink-500 rounded-full shadow-[0_0_10px_rgba(236,72,153,0.8)]"
               initial={{ left: '0%' }}
               animate={{ left: '40%' }}
               transition={{ duration: 1 }}
            />

            {/* Scanning Effect */}
            <motion.div 
               className="absolute left-[20%] top-0 bottom-0 w-1 bg-indigo-500/50 blur-sm"
               initial={{ left: '20%' }}
               animate={{ left: '45%' }}
               transition={{ duration: 1, yoyo: Infinity }}
            />

            {/* The Match */}
            <motion.div 
               className="absolute right-0 top-1/2 -translate-y-1/2 bg-indigo-500/20 border border-indigo-400 p-4 rounded-lg w-48 shadow-lg"
               initial={{ x: 50, opacity: 0 }}
               animate={{ x: 0, opacity: 1 }}
               transition={{ delay: 1.2 }}
            >
               <div className="flex items-center gap-2 mb-2 text-indigo-300">
                  <Sparkles className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase">Top Match Found</span>
               </div>
               <p className="text-sm text-indigo-100">"{data.retrievedContext}"</p>
               <span className="text-[10px] text-green-400 block mt-2 text-right">Similarity: 0.92</span>
            </motion.div>
          </motion.div>
        )}

        {/* Step 7: Generation */}
        {currentStep === PipelineStep.GENERATION && (
          <motion.div 
            key="generation"
            variants={containerVariants}
            initial="hidden" animate="visible" exit="exit"
            className="flex flex-col items-center w-full"
          >
             <div className="flex items-center justify-center gap-4 mb-8">
                {/* Inputs to LLM */}
                <div className="flex flex-col gap-2">
                   <div className="bg-pink-900/40 border border-pink-700 p-2 rounded text-xs text-pink-200 w-32 truncate">
                      Query: {data.query}
                   </div>
                   <div className="bg-indigo-900/40 border border-indigo-700 p-2 rounded text-xs text-indigo-200 w-32 truncate">
                      Ctx: {data.retrievedContext}
                   </div>
                </div>

                <div className="relative">
                   <ArrowRight className="text-slate-500" />
                </div>

                {/* The Brain */}
                <motion.div 
                   animate={{ scale: [1, 1.1, 1], filter: ["brightness(1)", "brightness(1.5)", "brightness(1)"] }}
                   transition={{ duration: 2, repeat: Infinity }}
                   className="relative"
                >
                   <Brain className="w-20 h-20 text-orange-500" />
                   <div className="absolute inset-0 bg-orange-500/30 blur-xl -z-10 rounded-full" />
                </motion.div>
             </div>

             {/* The Output */}
             <motion.div 
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 1.5 }}
                className="bg-gradient-to-r from-orange-500/10 to-amber-500/10 border border-orange-500/50 p-6 rounded-2xl max-w-md w-full"
             >
                <div className="flex items-center gap-2 mb-2">
                   <MessageSquare className="w-5 h-5 text-orange-400" />
                   <span className="font-semibold text-orange-200">AI Response</span>
                </div>
                <p className="text-lg text-white font-medium">
                   {data.finalAnswer}
                </p>
             </motion.div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
};

export default StepVisualizer;
