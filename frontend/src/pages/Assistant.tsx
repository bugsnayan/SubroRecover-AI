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

const formatClaimId = (id: string): string => {
  if (!id) return id;
  if (id.startsWith('CLM-')) {
    const num = id.replace('CLM-', '').padStart(5, '0');
    return `CN-2026-${num}`;
  }
  return id;
};

const renderInlineMarkdown = (text: string) => {
  const tokens: (string | React.ReactNode)[] = [];
  const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  const parts = text.split(regex);

  parts.forEach((part, index) => {
    if (!part) return;
    if (part.startsWith('**') && part.endsWith('**')) {
      tokens.push(
        <strong key={index} className="font-semibold text-navy-950 dark:text-paper-50">
          {part.slice(2, -2)}
        </strong>
      );
    } else if (part.startsWith('*') && part.endsWith('*')) {
      tokens.push(
        <em key={index} className="italic text-slate-700 dark:text-slate-300">
          {part.slice(1, -1)}
        </em>
      );
    } else if (part.startsWith('`') && part.endsWith('`')) {
      tokens.push(
        <code
          key={index}
          className="px-1.5 py-0.5 rounded bg-paper-200/80 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 font-mono text-[11px] text-brass-600 dark:text-brass-400"
        >
          {part.slice(1, -1)}
        </code>
      );
    } else {
      tokens.push(part);
    }
  });

  return tokens;
};

const MarkdownRenderer: React.FC<{ content: string }> = ({ content }) => {
  const paragraphs = content.split(/\n\n+/);

  return (
    <div className="space-y-2.5 font-sans">
      {paragraphs.map((p, pIdx) => {
        const lines = p.split('\n');
        const isBulletBlock = lines.some(
          (l) => l.trim().startsWith('• ') || l.trim().startsWith('- ') || l.trim().startsWith('* ')
        );

        if (isBulletBlock) {
          return (
            <ul key={pIdx} className="space-y-1.5 my-1">
              {lines.map((line, lIdx) => {
                const trimmed = line.trim();
                if (trimmed.startsWith('• ') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                  const bulletText = trimmed.replace(/^[•\-*]\s+/, '');
                  return (
                    <li key={lIdx} className="flex items-start gap-2 text-xs leading-relaxed">
                      <span className="w-1.5 h-1.5 rounded-full bg-brass-500 mt-1.5 flex-shrink-0" />
                      <span>{renderInlineMarkdown(bulletText)}</span>
                    </li>
                  );
                }
                return (
                  <p key={lIdx} className="text-xs leading-relaxed">
                    {renderInlineMarkdown(line)}
                  </p>
                );
              })}
            </ul>
          );
        }

        return (
          <p key={pIdx} className="text-xs leading-relaxed">
            {lines.map((line, lIdx) => (
              <React.Fragment key={lIdx}>
                {renderInlineMarkdown(line)}
                {lIdx < lines.length - 1 && <br />}
              </React.Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
};

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
                  <MarkdownRenderer content={m.text} />
                </div>

                {/* Grounded Evidence Citations (Sources list under every answer) */}
                {m.sources && m.sources.length > 0 && (
                  <div className="rounded-xl bg-paper-100/70 dark:bg-navy-900/90 border border-paper-200 dark:border-navy-800 text-xs overflow-hidden shadow-xs">
                    <div className="flex items-center justify-between px-3.5 py-2.5 bg-paper-200/50 dark:bg-navy-950/60 border-b border-paper-200 dark:border-navy-800/80 font-semibold text-slate-700 dark:text-slate-300">
                      <div className="flex items-center gap-1.5 font-mono text-[11px]">
                        <FileText className="w-3.5 h-3.5 text-brass-500" />
                        <span>Sources ({m.sources.length})</span>
                      </div>
                      <span className="text-[10px] font-mono text-teal-600 dark:text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20">
                        Indexed Documents
                      </span>
                    </div>
                    <div className="p-3 space-y-2">
                      {m.sources.map((s, sIdx) => {
                        const docTitle = s.title || (s as any).document || 'Accident Incident Dossier';
                        const docClaim = s.claim_id ? formatClaimId(s.claim_id) : undefined;
                        return (
                          <div
                            key={sIdx}
                            className="p-2.5 rounded-lg bg-paper-50 dark:bg-navy-950 border border-paper-200 dark:border-navy-800/80 text-[11px] space-y-1.5"
                          >
                            <div className="flex items-center justify-between font-semibold text-navy-950 dark:text-paper-100">
                              <span className="font-sans flex items-center gap-1.5">
                                <FileText className="w-3 h-3 text-brass-500" />
                                {docTitle}
                              </span>
                              <div className="flex items-center gap-2 font-mono text-[10px] text-slate-400">
                                {docClaim && <span className="text-brass-500">{docClaim}</span>}
                                <span>Page {s.page || 1}</span>
                              </div>
                            </div>
                            <p className="italic font-sans text-slate-600 dark:text-slate-300 leading-relaxed pl-4 border-l-2 border-brass-500/40">
                              "{s.snippet}"
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Open Claim Buttons */}
                {m.referencedClaims && m.referencedClaims.length > 0 && (
                  <div className="flex flex-wrap items-center gap-2 pt-0.5">
                    {m.referencedClaims.map((cid) => {
                      const cleanId = formatClaimId(cid);
                      return (
                        <button
                          key={cleanId}
                          onClick={() => navigate(`/claims/${cleanId}`)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brass-500/10 hover:bg-brass-500/20 text-brass-600 dark:text-brass-400 border border-brass-500/30 text-xs font-mono font-semibold transition-all shadow-sm cursor-pointer"
                        >
                          <span>Open claim {cleanId}</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      );
                    })}
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