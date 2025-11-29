import { useState, useRef, useEffect } from 'react';
import {
  FluentProvider,
  webDarkTheme,
  Text,
  Input,
  Button,
  Spinner,
  makeStyles,
  shorthands,
  Avatar
} from '@fluentui/react-components';
import {
  BotSparkle24Regular,
  Send24Regular,
  Mic24Regular,
  Attach24Regular
} from '@fluentui/react-icons';
import axios from 'axios';
import { useMsal, AuthenticatedTemplate, UnauthenticatedTemplate } from "@azure/msal-react";
import ExplanationGraph from './components/ExplanationGraph';
import { Login } from './components/Login';
import { TicketResponse, AgentMessage } from './types';
import './App.css';

const useStyles = makeStyles({
  appContainer: {
    display: 'flex',
    height: '100vh',
    backgroundColor: 'var(--bg-dark)',
    color: 'var(--text-primary)',
    overflow: 'hidden',
  },
  sidebar: {
    width: '260px',
    backgroundColor: 'rgba(10, 14, 23, 0.95)',
    borderRight: 'var(--glass-border)',
    display: 'flex',
    flexDirection: 'column',
    ...shorthands.padding('20px'),
    zIndex: 10,
  },
  mainContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
  },
  header: {
    height: '70px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    ...shorthands.padding('0', '30px'),
    borderBottom: 'var(--glass-border)',
    backgroundColor: 'rgba(10, 14, 23, 0.5)',
    backdropFilter: 'blur(10px)',
  },
  workspace: {
    flex: 1,
    display: 'flex',
    ...shorthands.padding('20px'),
    gap: '20px',
    overflow: 'hidden',
  },
  chatPanel: {
    flex: '0 0 450px',
    display: 'flex',
    flexDirection: 'column',
    borderRadius: '16px',
    overflow: 'hidden',
  },
  insightsPanel: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  messageList: {
    flex: 1,
    overflowY: 'auto',
    ...shorthands.padding('20px'),
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  inputContainer: {
    ...shorthands.padding('20px'),
    backgroundColor: 'rgba(20, 25, 35, 0.5)',
    borderTop: 'var(--glass-border)',
  },
  inputWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    ...shorthands.padding('8px', '12px'),
    borderRadius: '12px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    ':focus-within': {
      ...shorthands.borderColor('var(--primary-neon)'),
      boxShadow: '0 0 10px rgba(0, 240, 255, 0.2)',
    }
  },
  messageBubble: {
    maxWidth: '85%',
    ...shorthands.padding('14px', '18px'),
    borderRadius: '16px',
    fontSize: '14px',
    lineHeight: '1.5',
    animation: 'fade-in-up 0.3s ease-out',
  },
  userBubble: {
    alignSelf: 'flex-end',
    background: 'linear-gradient(135deg, #0078d4 0%, #00bcf2 100%)',
    color: 'white',
    borderBottomRightRadius: '4px',
  },
  agentBubble: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    color: 'var(--text-primary)',
    borderBottomLeftRadius: '4px',
  },
  statusCard: {
    ...shorthands.padding('20px'),
    borderRadius: '16px',
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '15px',
  },
  statItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '5px',
  },
  statLabel: {
    fontSize: '12px',
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '1px',
  },
  statValue: {
    fontSize: '18px',
    fontWeight: '600',
    color: 'var(--primary-neon)',
  }
});

const App: React.FC = () => {
  const styles = useStyles();
  const { accounts, instance } = useMsal();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [ticketData, setTicketData] = useState<TicketResponse | null>(null);
  const [isListening, setIsListening] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const userAccount = accounts[0];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: AgentMessage = {
      agent_type: 'USER' as any,
      content: input,
      timestamp: new Date().toISOString(),
      confidence: 1.0
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/v1/tickets', {
        description: input,
        user_id: userAccount?.username || 'user-123', // Use real email
        channel: 'web',
        priority: 'medium'
      });

      const data: TicketResponse = response.data;
      setTicketData(data);

      if (data.conversation && data.conversation.messages) {
        const newAgentMessages = data.conversation.messages.filter(m => m.agent_type !== 'USER' as any);
        setMessages(prev => [...prev, ...newAgentMessages]);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        agent_type: 'SYSTEM' as any,
        content: 'Error connecting to service desk. Please try again.',
        timestamp: new Date().toISOString(),
        confidence: 0
      }]);
    } finally {
      setLoading(false);
    }
  };

  const startListening = async () => {
    if (isListening) return;
    try {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.onstart = () => setIsListening(true);
        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput(transcript);
        };
        recognition.onend = () => setIsListening(false);
        recognition.start();
      } else {
        alert("Browser doesn't support speech recognition.");
      }
    } catch (error) {
      console.error(error);
      setIsListening(false);
    }
  };

  const handleLogout = () => {
    instance.logoutPopup().catch(e => {
      console.error(e);
    });
  };

  return (
    <FluentProvider theme={webDarkTheme}>
      <UnauthenticatedTemplate>
        <Login />
      </UnauthenticatedTemplate>

      <AuthenticatedTemplate>
        <div className={styles.appContainer}>
          {/* Sidebar */}
          <aside className={`${styles.sidebar} glass-panel`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px' }}>
              <div style={{ width: '32px', height: '32px', background: 'var(--primary-neon)', borderRadius: '8px' }}></div>
              <Text size={500} weight="bold" style={{ color: 'white' }}>ResolveIQ</Text>
            </div>

            <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {['Dashboard', 'My Tickets', 'Knowledge Base', 'Analytics', 'Settings'].map((item, i) => (
                <div key={item} style={{
                  padding: '12px',
                  borderRadius: '8px',
                  color: i === 0 ? 'var(--primary-neon)' : 'var(--text-secondary)',
                  background: i === 0 ? 'rgba(0, 240, 255, 0.1)' : 'transparent',
                  cursor: 'pointer'
                }}>
                  <Text>{item}</Text>
                </div>
              ))}
              <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <Button appearance="subtle" onClick={handleLogout} style={{ color: 'var(--text-muted)' }}>Sign Out</Button>
              </div>
            </nav>
          </aside>

          {/* Main Content */}
          <div className={styles.mainContent}>
            <header className={styles.header}>
              <Text size={400} weight="semibold" style={{ color: 'var(--text-secondary)' }}>
                Autonomous Enterprise Service Mesh
              </Text>
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <div style={{ textAlign: 'right' }}>
                  <Text block size={300} weight="semibold">{userAccount?.name || 'User'}</Text>
                  <Text block size={200} style={{ color: 'var(--text-muted)' }}>{userAccount?.username || 'Employee'}</Text>
                </div>
                <Avatar name={userAccount?.name || 'User'} color="brand" />
              </div>
            </header>

            <div className={styles.workspace}>
              {/* Chat Panel */}
              <section className={`${styles.chatPanel} glass-panel`}>
                <div className={styles.messageList}>
                  {messages.length === 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', opacity: 0.5 }}>
                      <BotSparkle24Regular style={{ fontSize: '48px', marginBottom: '10px', color: 'var(--primary-neon)' }} />
                      <Text>How can I help you today, {userAccount?.name?.split(' ')[0]}?</Text>
                    </div>
                  )}
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`${styles.messageBubble} ${msg.agent_type === 'USER' ? styles.userBubble : styles.agentBubble}`}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                        {msg.agent_type !== 'USER' && (
                          <Text size={200} style={{ color: 'var(--primary-neon)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                            {msg.agent_type}
                          </Text>
                        )}
                      </div>
                      <Text>{msg.content}</Text>
                    </div>
                  ))}
                  {loading && (
                    <div className={styles.agentBubble} style={{ padding: '10px', width: 'fit-content' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Spinner size="tiny" />
                        <Text size={200} style={{ color: 'var(--text-muted)' }}>Processing...</Text>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                <div className={styles.inputContainer}>
                  <div className={styles.inputWrapper}>
                    <Button appearance="transparent" icon={<Attach24Regular />} />
                    <Input
                      value={input}
                      onChange={(_, data) => setInput(data.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                      placeholder="Describe your issue..."
                      style={{ flex: 1, background: 'transparent', border: 'none', color: 'white' }}
                      input={{ style: { color: 'white' } }} // Fluent UI specific
                    />
                    <Button
                      appearance="transparent"
                      icon={<Mic24Regular />}
                      style={{ color: isListening ? 'red' : 'inherit' }}
                      onClick={startListening}
                    />
                    <Button
                      appearance="primary"
                      icon={<Send24Regular />}
                      onClick={handleSend}
                      disabled={loading || !input.trim()}
                      style={{ background: 'var(--primary-blue)' }}
                    />
                  </div>
                </div>
              </section>

              {/* Insights Panel */}
              <section className={styles.insightsPanel}>
                {/* Stats / Status */}
                <div className={`${styles.statusCard} glass-panel`}>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Status</span>
                    <span className={styles.statValue} style={{ color: ticketData?.ticket.status === 'resolved' ? '#10ff10' : 'white' }}>
                      {ticketData?.ticket.status.toUpperCase() || 'IDLE'}
                    </span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Category</span>
                    <span className={styles.statValue}>{ticketData?.ticket.category || '-'}</span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Confidence</span>
                    <span className={styles.statValue}>
                      {ticketData?.ticket.confidence_score ? `${(ticketData.ticket.confidence_score * 100).toFixed(0)}%` : '-'}
                    </span>
                  </div>
                  <div className={styles.statItem}>
                    <span className={styles.statLabel}>Ticket ID</span>
                    <span className={styles.statValue} style={{ fontSize: '14px', alignSelf: 'center' }}>
                      {ticketData?.ticket.id.split('-')[0] || '-'}...
                    </span>
                  </div>
                </div>

                {/* Graph */}
                <div className="glass-panel" style={{ flex: 1, borderRadius: '16px', padding: '20px', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                    <Text weight="semibold" style={{ color: 'var(--primary-neon)' }}>LIVE REASONING GRAPH</Text>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#00ff00', boxShadow: '0 0 5px #00ff00' }}></div>
                      <Text size={200} style={{ color: 'var(--text-muted)' }}>Active</Text>
                    </div>
                  </div>
                  <div style={{ flex: 1, border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '8px', overflow: 'hidden' }}>
                    {ticketData?.explanation_graph ? (
                      <ExplanationGraph data={ticketData.explanation_graph} />
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                        <Text>Waiting for input...</Text>
                      </div>
                    )}
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </AuthenticatedTemplate>
    </FluentProvider>
  );
}

export default App;
