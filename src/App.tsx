import React, { useState, useEffect, useRef } from 'react';
import { 
  Users, 
  Globe, 
  MessageSquare, 
  Plus, 
  Trash2, 
  ChevronRight, 
  Sparkles,
  Send,
  Loader2,
  Settings2,
  PenTool
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GoogleGenAI } from "@google/genai";
import Markdown from 'react-markdown';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Character, WorldSetting, StoryState, ChatMessage } from './types';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const INITIAL_STATE: StoryState = {
  title: 'Untitled Story',
  synopsis: '',
  characters: [],
  worldSettings: [],
  manuscript: ''
};

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'characters' | 'world' | 'manuscript'>('chat');
  const [story, setStory] = useState<StoryState>(() => {
    const saved = localStorage.getItem('novelcraft_story');
    return saved ? JSON.parse(saved) : INITIAL_STATE;
  });
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    localStorage.setItem('novelcraft_story', JSON.stringify(story));
  }, [story]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || '' });

  const generateAIResponse = async (prompt: string) => {
    setIsLoading(true);
    try {
      const model = "gemini-3.1-pro-preview";
      const systemInstruction = `You are a professional novel writing assistant. 
      Current Story Context:
      Title: ${story.title}
      Synopsis: ${story.synopsis}
      Characters: ${story.characters.map(c => `${c.name} (${c.role}): ${c.description}`).join('; ')}
      World Settings: ${story.worldSettings.map(w => `${w.title}: ${w.description}`).join('; ')}
      
      Your goal is to help the user develop their story. 
      - Propose creative ideas.
      - Maintain consistency with characters and world rules.
      - Ask clarifying questions to help the user make choices.
      - Help write scenes or dialogue when requested.
      - If the user asks for information, provide well-researched or creative answers.
      
      Always be encouraging and collaborative.
      Always respond in Thai unless specifically asked otherwise.`;

      const response = await ai.models.generateContent({
        model,
        contents: [
          ...messages.map(m => ({ role: m.role, parts: [{ text: m.content }] })),
          { role: 'user', parts: [{ text: prompt }] }
        ],
        config: {
          systemInstruction,
        },
      });

      const text = response.text || "I'm sorry, I couldn't generate a response.";
      setMessages(prev => [...prev, { role: 'model', content: text }]);
    } catch (error) {
      console.error("AI Error:", error);
      setMessages(prev => [...prev, { role: 'model', content: "Error: Failed to connect to AI. Please check your API key or network." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleManuscriptAI = async (action: 'continue' | 'rewrite') => {
    setIsLoading(true);
    try {
      const model = "gemini-3.1-pro-preview";
      const prompt = action === 'continue' 
        ? `Based on the current manuscript and context, write the next paragraph of the story. 
           Manuscript: ${story.manuscript}`
        : `Rewrite the following manuscript to be more engaging and descriptive, while keeping the same plot points.
           Manuscript: ${story.manuscript}`;

      const systemInstruction = `You are a professional novel writing assistant. 
      Current Story Context:
      Title: ${story.title}
      Synopsis: ${story.synopsis}
      Characters: ${story.characters.map(c => `${c.name} (${c.role}): ${c.description}. Goals: ${c.goals}`).join('; ')}
      World Settings: ${story.worldSettings.map(w => `${w.title}: ${w.description}`).join('; ')}
      
      Write in Thai. Maintain the tone and style of the existing manuscript if provided.`;

      const response = await ai.models.generateContent({
        model,
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        config: { systemInstruction },
      });

      const text = response.text || "";
      if (action === 'continue') {
        setStory(prev => ({ ...prev, manuscript: prev.manuscript + "\n\n" + text }));
      } else {
        setStory(prev => ({ ...prev, manuscript: text }));
      }
    } catch (error) {
      console.error("AI Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    await generateAIResponse(userMsg);
  };

  const handleBrainstorm = async () => {
    const prompt = "ช่วยเสนอไอเดียหรือแนวทางในการดำเนินเรื่องต่อจากข้อมูลที่มีอยู่หน่อย";
    setMessages(prev => [...prev, { role: 'user', content: prompt }]);
    await generateAIResponse(prompt);
  };

  const addCharacter = () => {
    const newChar: Character = {
      id: crypto.randomUUID(),
      name: 'ชื่อตัวละครใหม่',
      role: 'ตัวเอก',
      description: '',
      traits: [],
      goals: ''
    };
    setStory(prev => ({ ...prev, characters: [...prev.characters, newChar] }));
  };

  const updateCharacter = (id: string, updates: Partial<Character>) => {
    setStory(prev => ({
      ...prev,
      characters: prev.characters.map(c => c.id === id ? { ...c, ...updates } : c)
    }));
  };

  const deleteCharacter = (id: string) => {
    setStory(prev => ({
      ...prev,
      characters: prev.characters.filter(c => c.id !== id)
    }));
  };

  const addWorldSetting = () => {
    const newSetting: WorldSetting = {
      id: crypto.randomUUID(),
      title: 'สถานที่หรือกฎใหม่',
      description: '',
      rules: ''
    };
    setStory(prev => ({ ...prev, worldSettings: [...prev.worldSettings, newSetting] }));
  };

  const updateWorldSetting = (id: string, updates: Partial<WorldSetting>) => {
    setStory(prev => ({
      ...prev,
      worldSettings: prev.worldSettings.map(w => w.id === id ? { ...w, ...updates } : w)
    }));
  };

  const deleteWorldSetting = (id: string) => {
    setStory(prev => ({
      ...prev,
      worldSettings: prev.worldSettings.filter(w => w.id !== id)
    }));
  };

  return (
    <div className="flex h-screen bg-[#fdfcfb] text-[#1c1917] overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#e7e5e4] flex flex-col bg-white">
        <div className="p-6 border-bottom border-[#e7e5e4]">
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-500" />
            NovelCraft
          </h1>
          <p className="text-xs text-[#78716c] mt-1">ผู้ช่วยเขียนนิยาย AI</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          <button 
            onClick={() => setActiveTab('chat')}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              activeTab === 'chat' ? "bg-[#f5f5f4] text-black" : "text-[#78716c] hover:bg-[#fafaf9] hover:text-black"
            )}
          >
            <MessageSquare className="w-4 h-4" />
            คุยกับ AI
          </button>
          <button 
            onClick={() => setActiveTab('characters')}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              activeTab === 'characters' ? "bg-[#f5f5f4] text-black" : "text-[#78716c] hover:bg-[#fafaf9] hover:text-black"
            )}
          >
            <Users className="w-4 h-4" />
            ตัวละคร
          </button>
          <button 
            onClick={() => setActiveTab('world')}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              activeTab === 'world' ? "bg-[#f5f5f4] text-black" : "text-[#78716c] hover:bg-[#fafaf9] hover:text-black"
            )}
          >
            <Globe className="w-4 h-4" />
            โลกและฉาก
          </button>
          <button 
            onClick={() => setActiveTab('manuscript')}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
              activeTab === 'manuscript' ? "bg-[#f5f5f4] text-black" : "text-[#78716c] hover:bg-[#fafaf9] hover:text-black"
            )}
          >
            <PenTool className="w-4 h-4" />
            ต้นฉบับ
          </button>
        </nav>

        <div className="p-4 border-t border-[#e7e5e4]">
          <div className="bg-[#fafaf9] rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase tracking-wider font-bold text-[#a8a29e]">โปรเจกต์ปัจจุบัน</span>
              <Settings2 className="w-3 h-3 text-[#a8a29e]" />
            </div>
            <input 
              value={story.title}
              onChange={(e) => setStory(prev => ({ ...prev, title: e.target.value }))}
              placeholder="ชื่อเรื่อง"
              className="w-full bg-transparent font-medium text-sm focus:outline-none border-b border-transparent focus:border-amber-500/30 pb-1 mb-2"
            />
            <textarea 
              value={story.synopsis}
              onChange={(e) => setStory(prev => ({ ...prev, synopsis: e.target.value }))}
              placeholder="เรื่องย่อสั้นๆ..."
              className="w-full bg-transparent text-[11px] text-[#78716c] focus:outline-none resize-none h-16 leading-tight"
            />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative">
        <AnimatePresence mode="wait">
          {activeTab === 'chat' && (
            <motion.div 
              key="chat"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex-1 flex flex-col h-full"
            >
              <header className="px-8 py-4 border-b border-[#e7e5e4] flex items-center justify-between bg-white/80 backdrop-blur-sm sticky top-0 z-10">
                <h2 className="text-lg font-semibold italic serif">คุยกับ AI</h2>
                <div className="flex items-center gap-2 text-xs text-[#78716c]">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  AI พร้อมช่วยเหลือ
                </div>
              </header>

              <div className="flex-1 overflow-y-auto p-8 space-y-6">
                {messages.length === 0 && (
                  <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4">
                    <div className="w-16 h-16 bg-amber-50 rounded-full flex items-center justify-center">
                      <Sparkles className="w-8 h-8 text-amber-500" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold">เริ่มต้นการเดินทางของคุณ</h3>
                      <p className="text-[#78716c] mt-2">คุยกับ AI เกี่ยวกับไอเดีย ตัวละคร หรือขอให้ช่วยเขียนฉากต่างๆ ข้อมูลที่คุณตั้งค่าไว้ในแท็บอื่นๆ AI จะนำมาประกอบการตอบเสมอ</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2 w-full mt-4">
                      <button 
                        onClick={() => setInput("ช่วยคิดจุดหักมุมของเรื่องหน่อย")}
                        className="text-xs p-3 border border-[#e7e5e4] rounded-xl hover:bg-[#fafaf9] transition-colors text-left"
                      >
                        ช่วยคิดจุดหักมุม
                      </button>
                      <button 
                        onClick={() => setInput("ช่วยบรรยายฉากที่ดูลึกลับหน่อย")}
                        className="text-xs p-3 border border-[#e7e5e4] rounded-xl hover:bg-[#fafaf9] transition-colors text-left"
                      >
                        ช่วยบรรยายฉาก
                      </button>
                      <button 
                        onClick={handleBrainstorm}
                        className="text-xs p-3 border border-amber-200 bg-amber-50 rounded-xl hover:bg-amber-100 transition-colors text-left flex items-center gap-2 col-span-2"
                      >
                        <Sparkles className="w-3 h-3 text-amber-600" />
                        ระดมสมองกับ AI (เสนอแนวคิดใหม่ๆ)
                      </button>
                    </div>
                  </div>
                )}
                {messages.map((msg, i) => (
                  <div key={i} className={cn(
                    "flex gap-4 max-w-3xl",
                    msg.role === 'user' ? "ml-auto flex-row-reverse" : ""
                  )}>
                    <div className={cn(
                      "w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold",
                      msg.role === 'user' ? "bg-black text-white" : "bg-amber-100 text-amber-700"
                    )}>
                      {msg.role === 'user' ? 'U' : 'AI'}
                    </div>
                    <div className={cn(
                      "p-4 rounded-2xl text-sm leading-relaxed",
                      msg.role === 'user' ? "bg-black text-white" : "bg-white border border-[#e7e5e4] shadow-sm"
                    )}>
                      <div className="markdown-body">
                        <Markdown>{msg.content}</Markdown>
                      </div>
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>

              <div className="p-8 pt-0">
                <form 
                  onSubmit={handleSendMessage}
                  className="relative max-w-3xl mx-auto"
                >
                  <input 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask anything about your story..."
                    className="w-full pl-6 pr-14 py-4 bg-white border border-[#e7e5e4] rounded-2xl shadow-lg focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50 transition-all"
                  />
                  <button 
                    disabled={isLoading || !input.trim()}
                    className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-black text-white rounded-xl flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-zinc-800 transition-colors"
                  >
                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  </button>
                </form>
              </div>
            </motion.div>
          )}

          {activeTab === 'characters' && (
            <motion.div 
              key="characters"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="flex-1 flex flex-col h-full p-8 overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-3xl font-bold tracking-tight">ตัวละคร</h2>
                  <p className="text-[#78716c] mt-1">จัดการรายชื่อตัวละครในเรื่องของคุณ</p>
                </div>
                <button 
                  onClick={addCharacter}
                  className="flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg hover:bg-zinc-800 transition-colors text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  เพิ่มตัวละคร
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {story.characters.map(char => (
                  <div key={char.id} className="bg-white border border-[#e7e5e4] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow group">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 bg-[#f5f5f4] rounded-xl flex items-center justify-center text-xl">
                        👤
                      </div>
                      <button 
                        onClick={() => deleteCharacter(char.id)}
                        className="text-[#a8a29e] hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <input 
                      value={char.name}
                      onChange={(e) => updateCharacter(char.id, { name: e.target.value })}
                      placeholder="ชื่อตัวละคร"
                      className="text-lg font-bold w-full bg-transparent focus:outline-none border-b border-transparent focus:border-amber-500/30 mb-1"
                    />
                    <input 
                      value={char.role}
                      onChange={(e) => updateCharacter(char.id, { role: e.target.value })}
                      placeholder="บทบาท (เช่น พระเอก)"
                      className="text-xs font-medium text-amber-600 uppercase tracking-wider w-full bg-transparent focus:outline-none mb-2"
                    />
                    <div className="flex flex-wrap gap-1 mb-3">
                      <input 
                        value={char.traits.join(', ')}
                        onChange={(e) => updateCharacter(char.id, { traits: e.target.value.split(',').map(t => t.trim()) })}
                        placeholder="อุปนิสัย (แยกด้วยเครื่องหมาย , )"
                        className="text-[10px] bg-amber-50 text-amber-700 px-2 py-1 rounded border border-amber-100 w-full focus:outline-none"
                      />
                    </div>
                    <textarea 
                      value={char.description}
                      onChange={(e) => updateCharacter(char.id, { description: e.target.value })}
                      placeholder="คำบรรยายและปูมหลัง..."
                      className="w-full bg-[#fafaf9] rounded-xl p-3 text-sm min-h-[80px] focus:outline-none border border-transparent focus:border-[#e7e5e4] transition-all resize-none mb-3"
                    />
                    <div className="space-y-2">
                      <label className="text-[10px] uppercase tracking-widest font-bold text-[#a8a29e]">เป้าหมาย</label>
                      <input 
                        value={char.goals}
                        onChange={(e) => updateCharacter(char.id, { goals: e.target.value })}
                        placeholder="สิ่งที่ตัวละครต้องการ..."
                        className="w-full bg-[#fafaf9] rounded-lg px-3 py-2 text-xs focus:outline-none border border-transparent focus:border-[#e7e5e4]"
                      />
                    </div>
                  </div>
                ))}
                {story.characters.length === 0 && (
                  <div className="col-span-full py-20 border-2 border-dashed border-[#e7e5e4] rounded-3xl flex flex-col items-center justify-center text-[#a8a29e]">
                    <Users className="w-12 h-12 mb-4 opacity-20" />
                    <p>ยังไม่มีตัวละคร เริ่มต้นด้วยการเพิ่มตัวละครใหม่!</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'world' && (
            <motion.div 
              key="world"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="flex-1 flex flex-col h-full p-8 overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h2 className="text-3xl font-bold tracking-tight">โลกและฉาก</h2>
                  <p className="text-[#78716c] mt-1">กำหนดสถานที่ กฎเกณฑ์ และตำนานของเรื่อง</p>
                </div>
                <button 
                  onClick={addWorldSetting}
                  className="flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg hover:bg-zinc-800 transition-colors text-sm font-medium"
                >
                  <Plus className="w-4 h-4" />
                  เพิ่มรายละเอียด
                </button>
              </div>

              <div className="space-y-6 max-w-4xl">
                {story.worldSettings.map(setting => (
                  <div key={setting.id} className="bg-white border border-[#e7e5e4] rounded-2xl p-6 shadow-sm group">
                    <div className="flex items-center justify-between mb-4">
                      <input 
                        value={setting.title}
                        onChange={(e) => updateWorldSetting(setting.id, { title: e.target.value })}
                        placeholder="หัวข้อ (เช่น อาณาจักรเอลโดเรีย)"
                        className="text-xl font-bold w-full bg-transparent focus:outline-none border-b border-transparent focus:border-amber-500/30"
                      />
                      <button 
                        onClick={() => deleteWorldSetting(setting.id)}
                        className="text-[#a8a29e] hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-[10px] uppercase tracking-widest font-bold text-[#a8a29e] mb-2 block">คำบรรยาย</label>
                        <textarea 
                          value={setting.description}
                          onChange={(e) => updateWorldSetting(setting.id, { description: e.target.value })}
                          placeholder="บรรยายสถานที่หรือแนวคิด..."
                          className="w-full bg-[#fafaf9] rounded-xl p-3 text-sm min-h-[120px] focus:outline-none border border-transparent focus:border-[#e7e5e4] transition-all resize-none"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase tracking-widest font-bold text-[#a8a29e] mb-2 block">กฎและตำนาน</label>
                        <textarea 
                          value={setting.rules}
                          onChange={(e) => updateWorldSetting(setting.id, { rules: e.target.value })}
                          placeholder="กฎเฉพาะหรือประวัติศาสตร์..."
                          className="w-full bg-[#fafaf9] rounded-xl p-3 text-sm min-h-[120px] focus:outline-none border border-transparent focus:border-[#e7e5e4] transition-all resize-none"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                {story.worldSettings.length === 0 && (
                  <div className="py-20 border-2 border-dashed border-[#e7e5e4] rounded-3xl flex flex-col items-center justify-center text-[#a8a29e]">
                    <Globe className="w-12 h-12 mb-4 opacity-20" />
                    <p>ยังไม่มีข้อมูลโลก เริ่มต้นด้วยการเพิ่มรายละเอียดใหม่!</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'manuscript' && (
            <motion.div 
              key="manuscript"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="flex-1 flex flex-col h-full bg-[#f5f5f4] p-8 overflow-y-auto"
            >
              <div className="max-w-3xl mx-auto w-full bg-white shadow-xl rounded-sm min-h-screen p-16 flex flex-col">
                <div className="mb-12 text-center">
                  <input 
                    value={story.title}
                    onChange={(e) => setStory(prev => ({ ...prev, title: e.target.value }))}
                    className="text-4xl font-serif text-center w-full bg-transparent focus:outline-none mb-2"
                  />
                  <div className="h-px w-24 bg-black mx-auto mb-8" />
                </div>
                
                <textarea 
                  value={story.manuscript}
                  onChange={(e) => setStory(prev => ({ ...prev, manuscript: e.target.value }))}
                  placeholder="เริ่มเขียนผลงานชิ้นเอกของคุณที่นี่..."
                  className="flex-1 w-full bg-transparent focus:outline-none resize-none font-serif text-lg leading-relaxed placeholder:italic"
                />
                
                <div className="mt-12 pt-8 border-t border-[#e7e5e4] flex items-center justify-between text-[#a8a29e] text-xs">
                  <div className="flex gap-4">
                    <span>{story.manuscript.split(/\s+/).filter(x => x).length} คำ</span>
                    <span>{story.manuscript.length} ตัวอักษร</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <button 
                      onClick={() => handleManuscriptAI('rewrite')}
                      disabled={isLoading || !story.manuscript}
                      className="hover:text-black transition-colors flex items-center gap-1 disabled:opacity-50"
                    >
                      {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                      AI ช่วยเกลา
                    </button>
                    <button 
                      onClick={() => handleManuscriptAI('continue')}
                      disabled={isLoading}
                      className="hover:text-black transition-colors flex items-center gap-1 disabled:opacity-50"
                    >
                      {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <ChevronRight className="w-3 h-3" />}
                      เขียนต่อให้หน่อย
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;
