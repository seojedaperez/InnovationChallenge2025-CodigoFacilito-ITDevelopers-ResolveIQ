import React, { useState, useEffect, useRef } from 'react';
import {
    Text,
    Input,
    Button,
    makeStyles,
    shorthands,
    Spinner,
    Dialog,
    DialogSurface,
    DialogBody,
    DialogTitle,
    DialogContent,
    Switch,
    Badge
} from '@fluentui/react-components';
import {
    Send24Regular,
    Mic24Regular,
    Attach24Regular,
    BotSparkle24Regular,
    Clock24Regular,
    ErrorCircle24Regular,
    WifiWarning24Regular,
    Dismiss24Regular,
    BookOpen24Regular,
    Speaker224Regular,
    SpeakerOff24Regular
} from '@fluentui/react-icons';
import axios from 'axios';
import { useMsal } from "@azure/msal-react";
import { loginRequest } from '../authConfig';
import { useSettings } from '../context/SettingsContext';
import { RelatedArticles } from '../components/RelatedArticles';

const useStyles = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        gap: '20px',
    },
    content: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        height: '100%',
        width: '100%',
        '@media (max-width: 1200px)': {
            display: 'flex',
            flexDirection: 'column',
            overflowY: 'auto', // Enable page scrolling on mobile
            paddingRight: '5px', // Avoid scrollbar overlap
        },
    },
    chatPanel: {
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'var(--bg-card)',
        borderRadius: '16px',
        border: 'var(--glass-border)',
        overflow: 'hidden',
        position: 'relative',
        minWidth: '0', // Critical for Grid to allow shrinking
        '@media (max-width: 1200px)': {
            minWidth: 'auto',
            flex: 'none',
            minHeight: '60vh', // Take at least 60% of screen height
            height: 'auto',
            marginBottom: '20px',
        },
    },
    chatHeader: {
        ...shorthands.padding('20px'),
        borderBottom: 'var(--glass-border)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
    },
    rightPanel: {
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        minWidth: '0',
        height: '100%', // Force full height
        overflow: 'hidden',
        '@media (max-width: 1200px)': {
            minWidth: 'auto',
            flex: 'none',
            height: 'auto', // Let it grow naturally
            overflow: 'visible',
        },
    }
});

interface KBArticle {
    id: string;
    title: string;
    content: string;
    category: string;
    relevance_score?: number;
}

interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    status?: 'sending' | 'sent' | 'error' | 'pending';
    relatedArticles?: KBArticle[];
    category?: string;
    categories?: string[];
    priority?: string;
}

interface GraphNode {
    id: string;
    label: string;
    type: 'input' | 'process' | 'decision' | 'output';
    status?: string;
    details?: string;
}

interface GraphData {
    nodes: GraphNode[];
    edges: { id: string; source: string; target: string }[];
}

export const Dashboard: React.FC = () => {
    const { t, language, notifications, accessibility = { colorBlindMode: 'normal', wcagLevel: 'A' } } = useSettings();
    const styles = useStyles();
    const { instance, accounts } = useMsal();
    const userAccount = accounts[0];
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [graphData, setGraphData] = useState<GraphData | null>(null);
    const [clientInfo, setClientInfo] = useState<{ ip: string; country: string } | null>(null);
    const [selectedArticle, setSelectedArticle] = useState<KBArticle | null>(null);
    const [isTtsEnabled, setIsTtsEnabled] = useState(true);

    // Connection State
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [isBackendAvailable, setIsBackendAvailable] = useState(true);
    const [pendingQueue, setPendingQueue] = useState<Message[]>([]);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Network Status Listener
    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    // Fetch Client Info (IP/Country)
    useEffect(() => {
        const fetchClientInfo = async () => {
            try {
                const response = await axios.get('https://ipapi.co/json/');
                setClientInfo({
                    ip: response.data.ip,
                    country: response.data.country_name
                });
            } catch (error) {
                console.warn("Failed to fetch client info:", error);
            }
        };
        fetchClientInfo();
    }, []);

    // Backend Health Check
    useEffect(() => {
        const checkBackend = async () => {
            if (!isOnline) return; // Don't check if no internet
            try {
                await axios.get('/api/health', { timeout: 5000 });
                setIsBackendAvailable(true);
            } catch (error) {
                console.warn("Backend health check failed:", error);
                setIsBackendAvailable(false);
            }
        };

        // Check immediately and then every 10 seconds
        checkBackend();
        const interval = setInterval(checkBackend, 10000);
        return () => clearInterval(interval);
    }, [isOnline]);

    // Process Pending Queue
    useEffect(() => {
        if (isOnline && isBackendAvailable && pendingQueue.length > 0) {
            processQueue();
        }
    }, [isOnline, isBackendAvailable, pendingQueue]);

    const processQueue = async () => {
        const queueToProcess = [...pendingQueue];
        setPendingQueue([]); // Clear queue to avoid duplicates, will re-add if fail

        for (const msg of queueToProcess) {
            try {
                // Update status to sending
                setMessages(prev => prev.map(m => m.id === msg.id ? { ...m, status: 'sending' } : m));

                await sendMessageToBackend(msg.content, msg.id);

            } catch (error) {
                console.error("Failed to process queued message:", error);
                // Re-queue if failed
                setMessages(prev => prev.map(m => m.id === msg.id ? { ...m, status: 'pending' } : m));
                setPendingQueue(prev => [...prev, msg]);
            }
        }
    };

    const getAccessToken = async () => {
        if (!userAccount) return null;
        try {
            const response = await instance.acquireTokenSilent({
                ...loginRequest,
                account: userAccount
            });
            return response.accessToken;
        } catch (error) {
            console.error("Error acquiring token:", error);
            return null;
        }
    };

    // Text-to-Speech Helper
    const speakText = (text: string) => {
        if (!isTtsEnabled) return;
        if (!('speechSynthesis' in window)) return;

        // Cancel any current speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language === 'Spanish' ? 'es-ES' : 'en-US';

        // Try to select a good voice
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.lang.includes(language === 'Spanish' ? 'es' : 'en') && v.name.includes('Google'));
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        window.speechSynthesis.speak(utterance);
    };

    const sendMessageToBackend = async (text: string, messageId: string) => {
        const accessToken = await getAccessToken();



        // console.log('DEBUG: Sending request with language:', language);
        const response = await axios.post('/api/v1/chat', {
            user_id: userAccount?.username || 'guest',
            message: text,
            language: language, // Pass selected language to backend
            email_notifications: notifications.email,
            user_email: userAccount?.username,
            ip_address: clientInfo?.ip,
            country: clientInfo?.country
        }, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        // Update user message to sent
        setMessages(prev => prev.map(m => m.id === messageId ? { ...m, status: 'sent' } : m));

        // console.log("API Response Data:", response.data);
        // console.log("KB Articles:", response.data.kb_articles);

        const aiMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: response.data.response,
            timestamp: new Date(),
            relatedArticles: response.data.kb_articles,
            category: response.data.category,
            categories: response.data.categories,
            priority: response.data.priority
        };
        setMessages(prev => [...prev, aiMsg]);

        // Trigger TTS
        speakText(response.data.response);

        // Trigger browser notification if enabled
        if (notifications.browser && Notification.permission === "granted") {
            new Notification("ResolveIQ AI Agent", {
                body: response.data.response,
                icon: "/favicon.ico" // Assuming favicon exists, or we can omit
            });
        }

        if (response.data.explanation_graph) {
            setGraphData(response.data.explanation_graph);
        }
    };

    const handleMicClick = () => {
        if (isListening) {
            console.log("Stopping speech recognition manually.");
            setIsListening(false);
            return;
        }

        console.log("Starting speech recognition...");

        if (!('webkitSpeechRecognition' in window)) {
            alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
            return;
        }

        const SpeechRecognition = (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        // Set language based on current setting
        recognition.lang = language === 'Spanish' ? 'es-ES' : 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            console.log("Speech recognition started");
            setIsListening(true);
        };

        recognition.onend = () => {
            console.log("Speech recognition ended");
            setIsListening(false);
        };

        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            console.log("Transcript received:", transcript);
            setInput(transcript);
        };

        recognition.onerror = (event: any) => {
            console.error('Speech recognition error', event.error);
            setIsListening(false);
        };

        recognition.start();
    };

    // Keyboard Shortcut for Mic (Ctrl+M)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.key === 'm') {
                e.preventDefault();
                handleMicClick();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isListening, language]);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        console.log("handleFileChange triggered", event.target.files);
        const file = event.target.files?.[0];
        if (!file) return;

        setIsTyping(true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post('/api/v1/ocr', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data && response.data.text) {
                setInput(prev => (prev ? prev + '\n\n' : '') + response.data.text);
            }
        } catch (error) {
            console.error("Error uploading file for OCR:", error);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: t('Failed to process image. Please try again.'),
                timestamp: new Date(),
                status: 'error'
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
            // Reset file input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const [lastQuery, setLastQuery] = useState('');

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
            status: (!isOnline || !isBackendAvailable) ? 'pending' : 'sending'
        };

        setMessages(prev => [...prev, userMsg]);
        const currentInput = input;
        setLastQuery(currentInput);
        setInput('');

        if (!isOnline || !isBackendAvailable) {
            setPendingQueue(prev => [...prev, userMsg]);
            return;
        }

        setIsTyping(true);
        setGraphData(null);

        try {
            await sendMessageToBackend(currentInput, userMsg.id);
        } catch (error) {
            console.error('Error sending message:', error);
            // If network error, queue it
            if (axios.isAxiosError(error) && (!error.response || error.response.status >= 500)) {
                setMessages(prev => prev.map(m => m.id === userMsg.id ? { ...m, status: 'pending' } : m));
                setPendingQueue(prev => [...prev, userMsg]);
                setIsTyping(false);
                setIsBackendAvailable(false);
                return;
            }

            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: t('Sorry, I encountered an error processing your request.'),
                timestamp: new Date(),
                status: 'error'
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    const getStatusColor = () => {
        if (!isOnline) return '#ffc107'; // Offline - Yellow
        if (!isBackendAvailable) return '#ffc107'; // Backend down - Yellow
        return '#00ff00'; // All good
    };

    const getStatusText = () => {
        if (!isOnline) return t('Offline');
        if (!isBackendAvailable) return t('System Offline');
        return t('Active');
    };

    return (
        <div className={styles.container}>
            {/* Force Grid Layout via inline style as a failsafe, though class should work */}
            <div
                className={styles.content}
                style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
                    gap: '20px'
                }}
            >
                {/* Chat Panel */}
                <div className={styles.chatPanel} style={{ minWidth: 0 }}>
                    <div className={styles.chatHeader}>
                        <BotSparkle24Regular style={{ color: 'var(--primary-neon)' }} />
                        <div>
                            <Text weight="bold" block>AI Agent</Text>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: getStatusColor() }}></div>
                                <Text size={200} style={{ color: 'var(--text-muted)' }}>{getStatusText()}</Text>
                            </div>
                        </div>
                        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            {isTtsEnabled ? <Speaker224Regular /> : <SpeakerOff24Regular style={{ color: 'var(--text-muted)' }} />}
                            <Switch
                                checked={isTtsEnabled}
                                onChange={(_, data) => {
                                    setIsTtsEnabled(data.checked);
                                    if (!data.checked) {
                                        window.speechSynthesis.cancel();
                                    }
                                }}
                                label={isTtsEnabled ? "Voice On" : "Voice Off"}
                            />
                        </div>
                    </div>

                    <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        {messages.map((msg) => (
                            <div key={msg.id} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%' }}>
                                <div style={{
                                    backgroundColor: accessibility.colorBlindMode === 'high-contrast'
                                        ? '#000000' // Black background for high contrast
                                        : msg.role === 'user' ? 'var(--primary-blue)' : 'rgba(255,255,255,0.1)',
                                    color: accessibility.colorBlindMode === 'high-contrast' ? '#FFFFFF' : 'inherit', // White text for high contrast
                                    border: accessibility.colorBlindMode === 'high-contrast' ? '2px solid #FFFFFF' : (msg.status === 'pending' ? '1px dashed rgba(255,255,255,0.3)' : 'none'),
                                    padding: '12px 16px',
                                    borderRadius: '12px',
                                    borderBottomRightRadius: msg.role === 'user' ? '2px' : '12px',
                                    borderBottomLeftRadius: msg.role === 'assistant' ? '2px' : '12px',
                                    opacity: msg.status === 'pending' ? 0.7 : 1
                                }}>
                                    <Text>{msg.content}</Text>
                                    {(msg.categories?.length ? msg.categories : (msg.category ? [msg.category] : [])).length > 0 && (
                                        <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                            {(msg.categories?.length ? msg.categories : (msg.category ? [msg.category] : [])).map((cat, idx) => (
                                                <Badge key={idx} appearance="outline" color="brand">
                                                    {cat}
                                                </Badge>
                                            ))}
                                            {msg.priority && (
                                                <Badge
                                                    appearance="filled"
                                                    color={msg.priority.toLowerCase() === 'high' ? 'danger' : 'informative'}
                                                >
                                                    {msg.priority}
                                                </Badge>
                                            )}
                                        </div>
                                    )}
                                    {msg.relatedArticles && msg.relatedArticles.length > 0 && (
                                        <div style={{ marginTop: '10px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '8px', display: 'flex', flexDirection: 'column', gap: '5px' }}>
                                            {msg.relatedArticles.map((article) => (
                                                <Button
                                                    key={article.id}
                                                    size="small"
                                                    appearance="secondary"
                                                    icon={<BookOpen24Regular />}
                                                    onClick={() => setSelectedArticle(article)}
                                                    style={{ justifyContent: 'flex-start' }}
                                                >
                                                    {article.title}
                                                </Button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', gap: '4px', marginTop: '4px' }}>
                                    <Text size={100} style={{ color: 'var(--text-muted)' }}>
                                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </Text>
                                    {msg.status === 'pending' && <Clock24Regular style={{ fontSize: '12px', color: 'var(--text-muted)' }} />}
                                    {msg.status === 'error' && <ErrorCircle24Regular style={{ fontSize: '12px', color: '#ff5252' }} />}
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div style={{ alignSelf: 'flex-start', backgroundColor: 'rgba(255,255,255,0.1)', padding: '12px', borderRadius: '12px' }}>
                                <Spinner size="tiny" />
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Article Dialog */}
                    {selectedArticle && (
                        <Dialog open={!!selectedArticle} onOpenChange={() => setSelectedArticle(null)}>
                            <DialogSurface style={{ maxWidth: '600px', width: '90%' }}>
                                <DialogBody>
                                    <DialogTitle
                                        action={
                                            <Button appearance="subtle" aria-label="close" onClick={() => setSelectedArticle(null)}>Close</Button>
                                        }
                                    >
                                        {selectedArticle.title}
                                    </DialogTitle>
                                    <DialogContent>
                                        <div style={{ lineHeight: '1.6', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
                                            {selectedArticle.content}
                                        </div>
                                    </DialogContent>
                                </DialogBody>
                            </DialogSurface>
                        </Dialog>
                    )}

                    <div style={{ padding: '20px', backgroundColor: 'rgba(0,0,0,0.2)' }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            backgroundColor: 'rgba(255,255,255,0.05)',
                            borderRadius: '12px',
                            padding: '5px 10px',
                            border: '1px solid rgba(255,255,255,0.1)'
                        }}>
                            <Button
                                appearance="subtle"
                                icon={<Attach24Regular />}
                                disabled={!isOnline && !pendingQueue.length}
                                onClick={() => {
                                    console.log("Attachment button clicked");
                                    if (fileInputRef.current) {
                                        console.log("Triggering file input click");
                                        fileInputRef.current.click();
                                    } else {
                                        console.error("File input ref is null");
                                    }
                                }}
                                title={t('Attach image or document')}
                            />
                            <Input
                                style={{ flex: 1, border: 'none', background: 'transparent' }}
                                placeholder={isListening ? t('Listening...') : (!isOnline || !isBackendAvailable) ? t('Message will be queued...') : t('Describe your issue... (Ctrl+M to speak)')}
                                value={input}
                                onChange={(_e, data) => setInput(data.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            />
                            <Button
                                appearance={isListening ? "primary" : "subtle"}
                                style={isListening ? { backgroundColor: '#ea4335', color: 'white', borderColor: '#ea4335' } : {}}
                                icon={isListening ? <Dismiss24Regular /> : <Mic24Regular />}
                                title="Ctrl+M to toggle voice"
                                disabled={!isOnline}
                                onClick={handleMicClick}
                            />
                            <Button appearance="primary" icon={<Send24Regular />} onClick={handleSend} />
                        </div>
                    </div>
                    {/* Hidden File Input moved here */}
                    <input
                        type="file"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        accept="image/*,.pdf,.doc,.docx"
                        onChange={(e) => {
                            console.log("File input changed");
                            handleFileChange(e);
                        }}
                    />
                </div >

                {/* Insights Panel */}
                < div className={styles.rightPanel} style={{ minWidth: 0 }}>
                    <div className="glass-panel" style={{ padding: '20px', borderRadius: '16px', flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                        <Text weight="bold" size={400} style={{ color: 'var(--primary-neon)', marginBottom: '15px', display: 'block' }}>
                            {t('LIVE REASONING GRAPH')}
                        </Text>
                        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', gap: '15px', overflowY: 'auto', paddingRight: '10px' }}>
                            {(!isOnline || !isBackendAvailable) && !graphData ? (
                                <div style={{
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '20px',
                                    opacity: 0.7
                                }}>
                                    <WifiWarning24Regular style={{ fontSize: '48px', color: '#ff9800' }} />
                                    <div style={{ textAlign: 'center' }}>
                                        <Text weight="semibold" style={{ color: '#ff9800', letterSpacing: '1px' }}>
                                            {!isOnline ? 'CONNECTION LOST' : 'SYSTEM OFFLINE'}
                                        </Text>
                                        <Text size={200} style={{ display: 'block', color: 'var(--text-muted)', marginTop: '5px' }}>
                                            {t('Waiting for connection...')}
                                        </Text>
                                    </div>
                                </div>
                            ) : graphData ? (
                                graphData.nodes.map((node, index) => (
                                    <div key={node.id} style={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        gap: '5px',
                                        opacity: 0,
                                        animation: `fadeIn 0.5s ease forwards ${index * 0.15}s`,
                                        position: 'relative'
                                    }}>
                                        {/* Connecting Line */}
                                        {index < graphData.nodes.length - 1 && (
                                            <div style={{
                                                position: 'absolute',
                                                left: '15px',
                                                top: '35px',
                                                bottom: '-20px',
                                                width: '2px',
                                                backgroundColor: 'rgba(255,255,255,0.1)',
                                                zIndex: 0
                                            }} />
                                        )}

                                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', zIndex: 1 }}>
                                            {/* Node Icon/Number */}
                                            <div style={{
                                                width: '32px',
                                                height: '32px',
                                                borderRadius: '50%',
                                                backgroundColor: 'var(--bg-card)',
                                                border: `2px solid ${node.type === 'decision' ? 'var(--primary-neon)' : 'rgba(255,255,255,0.2)'}`,
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                fontSize: '14px',
                                                fontWeight: 'bold',
                                                color: node.type === 'decision' ? 'var(--primary-neon)' : 'var(--text-primary)',
                                                boxShadow: '0 0 10px rgba(0,0,0,0.3)'
                                            }}>
                                                {index + 1}
                                            </div>

                                            {/* Node Content Card */}
                                            <div style={{
                                                backgroundColor: 'rgba(255,255,255,0.03)',
                                                padding: '12px',
                                                borderRadius: '8px',
                                                flex: 1,
                                                border: '1px solid rgba(255,255,255,0.05)',
                                                backdropFilter: 'blur(10px)'
                                            }}>
                                                <Text weight="semibold" size={300} style={{ display: 'block', marginBottom: '4px' }}>
                                                    {node.label}
                                                </Text>
                                                {node.details && (
                                                    <Text size={200} style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                                                        {node.details}
                                                    </Text>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div style={{
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '20px',
                                    opacity: 0.7
                                }}>
                                    <div style={{
                                        width: '60px',
                                        height: '60px',
                                        borderRadius: '50%',
                                        backgroundColor: 'rgba(0, 255, 242, 0.1)',
                                        border: '1px solid var(--primary-neon)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        animation: 'pulse 2s infinite'
                                    }}>
                                        <div style={{
                                            width: '10px',
                                            height: '10px',
                                            borderRadius: '50%',
                                            backgroundColor: 'var(--primary-neon)'
                                        }} />
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Related Articles */}
                        {/* Related Articles */}
                        <div style={{ flexShrink: 0, maxHeight: '40%' }}>
                            <RelatedArticles
                                query={input || lastQuery}
                                language={language}
                                onArticleClick={(article) => {
                                    setInput(prev => prev + (prev ? '\n' : '') + `Reference: ${article.title}`);
                                }}
                            />
                        </div>
                    </div>
                </div >
            </div >
        </div >
    );
};
