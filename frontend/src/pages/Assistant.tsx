import React, { useState, useRef, useEffect, useMemo } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Bot,
  Send,
  User,
  Sparkles,
  ExternalLink,
  FileText,
  Database,
  ChevronRight,
} from 'lucide-react';

import { api } from '../api/client';
import { ChatResponse, ChatSource } from '../types';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  sources?: ChatSource[];
  suggestedQuestions?: string[];
  referencedClaims?: string[];
  timestamp: string;
}

export const Assistant: React.FC = () => {
  const navigate = useNavigate();
  const [inputQuery, setInputQuery] = useState('');

  // Fetch top-5 needs-attention claims to dynamically generate suggested inquiries
  const { data: needsAttention } = useQuery({
    queryKey: ['needs-attention-assistant'],
    queryFn: () => api.getNeedsAttention(5),
  });

  const dynamicSuggestedQuestions = useMemo(() => {
    if (needsAttention && needsAttention.length > 0) {
      const qList: string[] = [];
      const c0 = needsAttention[0];
      qList.push(`What evidence supports adverse liability on claim ${c0.claim_number}?`);
      if (needsAttention.length > 1) {
        const c1 = needsAttention[1];
        qList.push(`Review recovery potential for ${c1.claim_number} (${c1.incident_type})`);
      }
      if (needsAttention.length > 2) {
        const c2 = needsAttention[2];
        qList.push(`What is the statute of limitations deadline for ${c2.claim_number}?`);
      } else {
        qList.push('How does the Make-Whole doctrine protect policyholder deductibles?');
      }
      return qList;
    }
    return [
      'Which claims have high recovery potential and impending SOL deadlines?',
      'How does the Make-Whole doctrine protect policyholder deductibles?',
      'What evidence supports adverse liability on high-priority claims?',
    ];
  }, [needsAttention]);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello. I am the SubroRecover AI Subrogation Intelligence Assistant. I am grounded directly on verified crash reports, police incident narratives, and evidence documents indexed in the evidence database. How can I assist your investigation today?',
      // No referenced cases on greeting
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const chatMutation = useMutation({
    mutationFn: (query: string) => api.sendChatMessage(query),
    onSuccess: (data: ChatResponse) => {
      const assistantMessage: Message = {
        id: Math.random().toString(),
        sender: 'assistant',
        text: data.answer,
        sources: data.sources && data.sources.length > 0 ? data.sources : undefined,
        suggestedQuestions: data.suggested_questions,
        referencedClaims: data.referenced_claims && data.referenced_claims.length > 0 ? data.referenced_claims : undefined,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
  });

  const handleSend = (textToSend?: string) => {
    const query = textToSend || inputQuery;
    if (!query.trim()) return;

    const userMessage: Message = {
      id: Math.random().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInputQuery('');
    chatMutation.mutate(query);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl shadow-sm overflow-hidden">
      {/* Chat Header with Plain Language Subtitle */}
      <div className="p-4 border-b border-paper-200 dark:border-navy-700/80 bg-paper-100/50 dark:bg-navy-900/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brass-500/20 text-brass-500 border border-brass-500/30 flex items-center justify-center shadow-glow-brass">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-navy-950 dark:text-paper-100 flex items-center gap-2">
              <span>SubroRecover AI assistant</span>
              <span className="text-[10px] font-mono font-normal px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/20">
                Grounded on ChromaDB
              </span>
            </h2>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-sans">
              Ask about claims, evidence and liability. Answers cite the source documents.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono hidden sm:flex">
          <Database className="w-3.5 h-3.5 text-brass-500" />
          <span>Evidence collection active</span>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.map((m, idx) => {
          const isUser = m.sender === 'user';
          const suggestedForThis =
            m.suggestedQuestions && m.suggestedQuestions.length > 0
              ? m.suggestedQuestions
              : idx === 0
              ? dynamicSuggestedQuestions
              : undefined;

          return (
            <div
              key={m.id}
              className={`flex gap-3.5 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-xs ${
                  isUser
                    ? 'bg-navy-800 dark:bg-paper-100 text-paper-100 dark:text-navy-950 font-bold'
                    : 'bg-brass-500 text-navy-950 shadow-glow-brass'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div className="space-y-2.5 flex-1 min-w-0">
                <div
                  className={`p-4 rounded-2xl text-xs leading-relaxed ${
                    isUser
                      ? 'bg-brass-500/15 border border-brass-500/30 text-navy-950 dark:text-paper-100'
                      : 'bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-800 text-navy-950 dark:text-paper-100 shadow-sm'
                  }`}
                >
                  <p className="whitespace-pre-line font-sans">{m.text}</p>
                </div>

                {/* Grounded Evidence Citations (Expandable Details) */}
                {m.sources && m.sources.length > 0 && (
                  <details className="group rounded-xl bg-paper-100/60 dark:bg-navy-900 border border-paper-200 dark:border-navy-800 text-xs overflow-hidden">
                    <summary className="flex items-center justify-between p-3 cursor-pointer select-none font-semibold text-slate-700 dark:text-slate-300 hover:text-brass-500 transition-colors">
                      <div className="flex items-center gap-1.5 font-mono text-[11px]">
                        <FileText className="w-3.5 h-3.5 text-brass-500" />
                        <span>Sources ({m.sources.length})</span>
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-open:rotate-90 transition-transform" />
                    </summary>
                    <div className="p-3 pt-0 space-y-2">
                      {m.sources.map((s, sIdx) => {
                        const docTitle = s.title || (s as any).document || 'Accident Incident Dossier';
                        return (
                          <div
                            key={sIdx}
                            className="p-2.5 rounded-lg bg-paper-200/50 dark:bg-navy-950 border border-paper-300 dark:border-navy-800/80 text-[11px] space-y-1"
                          >
                            <div className="flex items-center justify-between font-semibold text-navy-950 dark:text-paper-200">
                              <span className="font-sans">{docTitle}</span>
                              <span className="font-mono text-slate-400 text-[10px]">
                                Page {s.page}
                              </span>
                            </div>
                            <p className="italic font-sans text-slate-600 dark:text-slate-300 line-clamp-3">
                              "{s.snippet}"
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </details>
                )}

                {/* Open Claim Buttons */}
                {m.referencedClaims && m.referencedClaims.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2 pt-0.5">
                    {m.referencedClaims.map((cid) => (
                      <button
                        key={cid}
                        onClick={() => navigate(`/claims/${cid}`)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brass-500/10 hover:bg-brass-500/20 text-brass-600 dark:text-brass-400 border border-brass-500/30 text-xs font-mono font-semibold transition-all shadow-sm"
                      >
                        <span>Open claim {cid}</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    ))}
                  </div>
                )}

                {/* Dynamically Generated Suggested Inquiries */}
                {suggestedForThis && suggestedForThis.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[10px] font-semibold text-slate-400 block font-mono">
                      Suggested inquiries
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {suggestedForThis.map((q, qIdx) => (
                        <button
                          key={qIdx}
                          onClick={() => handleSend(q)}
                          className="text-left text-xs text-slate-600 dark:text-slate-300 bg-paper-200/60 dark:bg-navy-900/80 hover:bg-brass-500/15 hover:text-brass-500 border border-paper-300 dark:border-navy-700/60 px-3 py-1.5 rounded-xl transition-all font-sans"
                        >
                          {q} →
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {chatMutation.isPending && (
          <div className="flex gap-3 max-w-md">
            <div className="w-8 h-8 rounded-xl bg-brass-500 text-navy-950 flex items-center justify-center">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="p-3.5 rounded-2xl bg-paper-100 dark:bg-navy-950 border border-paper-200 dark:border-navy-800 text-xs font-mono text-slate-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brass-500 animate-pulse" />
              <span>Querying vector store & synthesizing evidence...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Query Input Bar */}
      <div className="p-4 border-t border-paper-200 dark:border-navy-700/80 bg-paper-100/60 dark:bg-navy-900/60">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask about claims, evidence and liability..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={chatMutation.isPending}
            className="flex-1 px-4 py-3 rounded-xl bg-paper-50 dark:bg-navy-950 border border-paper-300 dark:border-navy-700 text-xs text-navy-950 dark:text-paper-100 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brass-500 shadow-inner font-sans"
          />
          <button
            type="submit"
            disabled={!inputQuery.trim() || chatMutation.isPending}
            className="p-3 rounded-xl bg-brass-500 hover:bg-brass-600 disabled:opacity-40 disabled:cursor-not-allowed text-navy-950 font-bold shadow-glow-brass transition-all"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};