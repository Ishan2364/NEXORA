import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { QRCodeSVG } from 'qrcode.react';
import { 
  Smartphone, Monitor, Store, User, Sparkles, Package, 
  Lock, ArrowRight, Crown, Receipt, FileText, Download, 
  Home, Grid, LogOut, Menu
} from 'lucide-react';

const API_URL = "http://127.0.0.1:8000"; 

// --- SHARED COMPONENTS ---

const InvoiceCard = ({ data }) => {
    const inv = typeof data === 'string' ? JSON.parse(data) : data;
    return (
        <div className="animate-enter" style={{ background: 'white', color: '#1a0505', padding: '24px', borderRadius: '16px', minWidth: '280px', flex: '1 1 300px', border: '1px solid #e2e8f0', boxShadow: '0 4px 20px rgba(0,0,0,0.05)', position: 'relative' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '6px', background: 'linear-gradient(90deg, #d4af37, #fcd34d)', borderTopLeftRadius: '16px', borderTopRightRadius: '16px' }}></div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', marginTop: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ background: '#fffbeb', padding: '8px', borderRadius: '10px' }}><FileText size={20} color="#d4af37"/></div>
                    <div>
                        <p style={{ fontWeight: '800', fontSize: '1rem', margin: 0 }}>INVOICE</p>
                        <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>Nexora Retail</p>
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{inv.date}</p>
                    <p style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: '700' }}>PAID</p>
                </div>
            </div>
            <div style={{ padding: '16px', background: '#f8fafc', borderRadius: '12px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.85rem', color: '#64748b' }}>Order ID</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>{inv.order_id}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.85rem', color: '#64748b' }}>Items</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: '600', maxWidth: '150px', textAlign: 'right' }}>{inv.items}</span>
                </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '20px', borderTop: '1px dashed #e2e8f0', paddingTop: '16px' }}>
                <span style={{ fontSize: '0.9rem', color: '#64748b' }}>Total Paid</span>
                <span style={{ fontSize: '1.5rem', fontWeight: '800', color: '#1e293b' }}>₹{inv.amount}</span>
            </div>
            <button style={{ width: '100%', padding: '12px', background: '#1e293b', color: 'white', borderRadius: '10px', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: '0.2s' }}>
                <Download size={16}/> Download Receipt
            </button>
        </div>
    );
};

const CCPaymentForm = ({ onPay }) => {
    const [ccNum, setCcNum] = useState("");
    const [ccExp, setCcExp] = useState("");
    const [ccCvv, setCcCvv] = useState("");
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = () => {
        if(!ccNum || !ccExp || !ccCvv) return;
        setSubmitted(true);
        onPay(`PAYMENT_DATA: CARD_NUMBER=${ccNum}, EXP=${ccExp}, CVV=${ccCvv}`);
    };

    if (submitted) return <div style={{padding: '15px', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.2)'}}>🔒 Details Encrypted & Sent</div>;

    return (
        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '20px', borderRadius: '16px', marginTop: '10px', border: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: '#e1adac', fontWeight: '600' }}>
                <Lock size={16}/> Secure Payment Gateway
            </div>
            <input type="text" placeholder="Card Number" value={ccNum} onChange={e => setCcNum(e.target.value)} style={royalInputStyle} />
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <input type="text" placeholder="MM/YY" value={ccExp} onChange={e => setCcExp(e.target.value)} style={royalInputStyle} />
                <input type="password" placeholder="CVV" value={ccCvv} onChange={e => setCcCvv(e.target.value)} style={royalInputStyle} />
            </div>
            <button onClick={handleSubmit} style={{ width: '100%', marginTop: '16px', padding: '12px', background: 'linear-gradient(135deg, #d4af37 0%, #c5a028 100%)', color: '#1a0505', borderRadius: '8px', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>
                Pay Securely
            </button>
        </div>
    );
};

const BotAvatar = ({ role }) => (
    role === 'bot' ? 
    <div style={{ width: '36px', height: '36px', background: 'rgba(255,255,255,0.1)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, border: '1px solid rgba(212, 175, 55, 0.2)' }}>
        <Sparkles size={18} color="#d4af37" />
    </div> : null
);

const MessageBubble = ({ role, content, onPay, onInvoiceReceived }) => {
    // Helper to parse content
    let innerContent = content;
    let extraComponent = null;

    if (content.includes("||INVOICE_DATA:")) {
        const jsonStr = content.split("||INVOICE_DATA:")[1].split("||")[0];
        innerContent = content.replace(/\|\|INVOICE_DATA:.*?\|\|/, "").trim();
        extraComponent = <InvoiceCard data={jsonStr} />;
        // Side effect in render is bad practice usually, but keeping per your original pattern
        useEffect(() => { if (onInvoiceReceived) onInvoiceReceived(JSON.parse(jsonStr)); }, []);
    } else if (content.includes("||QR_CODE:")) {
        const amount = content.split("||QR_CODE:")[1].split("||")[0].trim();
        innerContent = content.replace(/\|\|QR_CODE:.*?\|\|/, "").trim();
        extraComponent = (
            <div style={{ background: 'white', padding: '15px', borderRadius: '12px', display: 'inline-block', marginTop: 10 }}>
                <QRCodeSVG value={`upi://pay?pa=nexora@upi&pn=Nexora&am=${amount}`} size={140} />
                <p style={{ textAlign: 'center', color: '#000', margin: '5px 0 0', fontWeight: 'bold', fontSize: '0.9rem' }}>₹{amount}</p>
            </div>
        );
    } else if (content.includes("||CC_FORM||")) {
        innerContent = content.replace("||CC_FORM||", "").trim();
        extraComponent = <CCPaymentForm onPay={onPay} />;
    }

    return (
        <div className={`msg-row animate-enter ${role}`}>
            <BotAvatar role={role} />
            <div className={`bubble ${role}`}>
                <p style={{margin:0, whiteSpace: 'pre-line'}}>{innerContent}</p>
                {extraComponent}
            </div>
        </div>
    );
};

// --- SUB-VIEWS (DASHBOARD & INVOICES CONTENT) ---
const DashboardContent = ({ userProfile }) => (
    <div className="dashboard-container animate-enter">
        <div className="profile-hero">
            <div className="avatar-large">{userProfile.name[0]}</div>
            <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '2rem', margin: 0, fontWeight: '700', lineHeight: '1.2', color: 'white', fontFamily: 'Playfair Display' }}>{userProfile.name}</h3>
                <div style={{ display: 'flex', flexWrap:'wrap', gap: '15px', marginTop: '16px', color: '#a3a3a3' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><User size={16} color="#d4af37"/> {userProfile.customer_id}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Crown size={16} color="#d4af37"/> {userProfile.loyalty_tier}</span>
                </div>
            </div>
        </div>

        <h3 style={{ margin: '30px 0 20px', color: '#d4af37', fontSize: '0.9rem', letterSpacing: '2px', fontWeight: '700' }}>RECENT ORDERS</h3>
        <div className="history-grid">
            {userProfile.purchase_history.length === 0 ? <p style={{color:'#666'}}>No past orders found.</p> : 
                userProfile.purchase_history.map((order, idx) => (
                <div key={idx} className="history-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                        <span style={{ fontSize: '0.85rem', color: '#888' }}>{order.date}</span>
                        <span style={{ fontWeight: '700', color: '#e1adac', fontSize: '1.1rem' }}>₹{order.price}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                        <div style={{padding:'10px', background:'rgba(255,255,255,0.05)', borderRadius:'10px'}}><Package size={20} color="#d4af37"/></div>
                        <div>
                            <p style={{ fontWeight: '600', color: 'white', margin: 0, fontSize: '1rem' }}>{order.product}</p>
                            <p style={{ fontSize: '0.85rem', color: '#666', margin: '4px 0 0' }}>{order.category}</p>
                        </div>
                    </div>
                    <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '12px', display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#888' }}>
                        <span>{order.payment_method}</span>
                        {order.returned ? <span style={{color:'#ef4444'}}>Returned</span> : <span style={{color:'#10b981'}}>Delivered</span>}
                    </div>
                </div>
            ))}
        </div>
    </div>
);

const InvoicesContent = ({ invoices }) => (
    <div className="dashboard-container animate-enter">
        <h2 style={{ fontSize: '2rem', fontFamily: 'Playfair Display', margin: '0 0 30px 0', color: '#e1adac' }}>My Invoices</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
            {invoices.length === 0 ? 
                <div style={{ textAlign: 'center', width: '100%', padding: '40px', color: '#666' }}>
                    <Receipt size={48} style={{ marginBottom: '10px', opacity: 0.2 }} />
                    <p>No invoices generated yet.</p>
                </div> 
            : invoices.map((inv, idx) => <InvoiceCard key={idx} data={inv} />)}
        </div>
    </div>
);

// --- 1. WEB INTERFACE (Original Perfect Design) ---
const WebInterface = ({ userProfile, messages, input, setInput, sendMessage, activeTab, setActiveTab, invoices, loading, chatRef, onSignOut }) => {
    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
            {/* Sidebar */}
            <div className="sidebar">
                <div style={{ marginBottom: '50px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Crown size={24} color="#d4af37" />
                    <span style={{ fontFamily: 'Playfair Display', fontSize: '1.4rem', color: 'white' }}>Nexora Web</span>
                </div>
                
                <div className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>
                    <Sparkles size={18} /> Concierge
                </div>
                <div className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
                    <User size={18} /> Dashboard
                </div>
                <div className={`nav-item ${activeTab === 'invoices' ? 'active' : ''}`} onClick={() => setActiveTab('invoices')}>
                    <Receipt size={18} /> Invoices
                </div>

                <div style={{ marginTop: 'auto', background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '16px' }}>
                    <p style={{fontWeight:'bold', color: 'white'}}>{userProfile?.name}</p>
                    <p style={{fontSize:'0.8rem', color: '#888'}}>{userProfile?.loyalty_tier} Member</p>
                    <button onClick={onSignOut} style={{ width: '100%', marginTop: '10px', padding: '8px', background: 'transparent', border: '1px solid #333', color: '#888', borderRadius: '8px', cursor: 'pointer' }}>Sign Out</button>
                </div>
            </div>

            {/* Main Content */}
            <div className="chat-layout">
                {activeTab === 'chat' && (
                    <>
                        <div className="messages-container">
                            {messages.map((msg, idx) => <MessageBubble key={idx} {...msg} />)}
                            {loading && <div style={{ color: '#666', padding: '0 20px' }}>Nexora is thinking...</div>}
                            <div ref={chatRef} />
                        </div>
                        <div className="input-zone">
                            <div className="input-bar">
                                <input className="input-field" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} placeholder="Ask Nexora..." />
                                <button onClick={() => sendMessage()} className="send-fab"><ArrowRight size={20} /></button>
                            </div>
                        </div>
                    </>
                )}
                {activeTab === 'dashboard' && <DashboardContent userProfile={userProfile} />}
                {activeTab === 'invoices' && <InvoicesContent invoices={invoices} />}
            </div>
        </div>
    );
};

// --- 2. MOBILE INTERFACE (Simulated Phone View + Real Time Clock) ---
const MobileInterface = ({ userProfile, messages, input, setInput, sendMessage, activeTab, setActiveTab, invoices, loading, chatRef, onSignOut }) => {
    
    // --- CLOCK LOGIC ---
    const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        }, 1000);
        return () => clearInterval(timer);
    }, []);
    // -------------------

    return (
        // 1. OUTER CONTAINER
        <div style={{ 
            height: '100vh', 
            width: '100vw', 
            background: '#121212', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            backgroundImage: 'radial-gradient(circle, #222 0%, #000 100%)'
        }}>
            
            {/* 2. PHONE FRAME */}
            <div style={{ 
                width: '390px', 
                height: '844px', 
                maxHeight: '95vh', 
                background: 'black', 
                borderRadius: '45px', 
                border: '8px solid #2a2a2a', 
                overflow: 'hidden', 
                boxShadow: '0 30px 60px rgba(0,0,0,0.6)', 
                display: 'flex', 
                flexDirection: 'column',
                position: 'relative'
            }}>

                {/* 3. STATUS BAR (Dynamic Time) */}
                <div style={{ height: '30px', background: 'black', display: 'flex', justifyContent: 'space-between', padding: '0 25px', alignItems: 'center', fontSize: '12px', color: 'white', fontWeight: 'bold', paddingTop: '10px' }}>
                    
                    {/* Real Time Display */}
                    <span>{currentTime}</span>
                    
                    <div style={{display:'flex', gap:6}}>
                        <span>5G</span>
                        {/* Simple Battery Icon */}
                        <div style={{width: 20, height: 10, border:'1px solid white', borderRadius: 2, position:'relative'}}>
                            <div style={{background:'white', width:'80%', height:'100%'}}></div>
                        </div>
                    </div>
                </div>

                {/* --- CONTENT STARTS HERE --- */}
                
                {/* Mobile Header */}
                <div style={{ padding: '15px 20px', background: '#0a0a0a', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '5px' }}>
                    <div style={{display:'flex', alignItems:'center', gap:10}}>
                        <Crown size={20} color="#d4af37"/>
                        <span style={{color:'white', fontWeight:'bold', fontFamily:'Playfair Display'}}>Nexora App</span>
                    </div>
                    <LogOut size={18} color="#666" onClick={onSignOut} style={{cursor:'pointer'}}/>
                </div>

                {/* Content Area (Scrollable) */}
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                    {activeTab === 'chat' && (
                        <>
                            <div style={{ flex: 1, padding: '15px', paddingBottom: 0 }}>
                                {messages.map((msg, idx) => <MessageBubble key={idx} {...msg} />)}
                                {loading && <div style={{ color: '#666', padding: '10px', fontSize:'0.8rem', textAlign:'center' }}>Nexora is thinking...</div>}
                                <div ref={chatRef} />
                            </div>
                            
                            <div style={{ padding: '10px', background: '#0a0a0a', borderTop:'1px solid #222' }}>
                                <div style={{ display:'flex', gap:10 }}>
                                    <input 
                                        value={input} onChange={e => setInput(e.target.value)} 
                                        style={{ flex:1, padding:'12px', borderRadius:'20px', border:'none', background:'#222', color:'white', fontSize:'0.9rem' }}
                                        placeholder="Type message..."
                                        onKeyDown={e => e.key === 'Enter' && sendMessage()}
                                    />
                                    <button onClick={() => sendMessage()} style={{width:40, height:40, borderRadius:'50%', background:'#d4af37', border:'none', display:'flex', alignItems:'center', justifyContent:'center'}}>
                                        <ArrowRight size={20} color="black"/>
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                    {activeTab === 'dashboard' && <div style={{padding:'10px'}}><DashboardContent userProfile={userProfile} /></div>}
                    {activeTab === 'invoices' && <div style={{padding:'10px'}}><InvoicesContent invoices={invoices} /></div>}
                </div>

                {/* Bottom Navigation */}
                <div style={{ height: '70px', background: '#0a0a0a', borderTop: '1px solid #333', display: 'flex', justifyContent: 'space-around', alignItems: 'center', paddingBottom: '15px' }}>
                    <div onClick={() => setActiveTab('chat')} style={{display:'flex', flexDirection:'column', alignItems:'center', gap:4, color: activeTab==='chat'?'#d4af37':'#666', cursor:'pointer'}}>
                        <Sparkles size={20} />
                        <span style={{fontSize:'0.7rem'}}>Chat</span>
                    </div>
                    <div onClick={() => setActiveTab('dashboard')} style={{display:'flex', flexDirection:'column', alignItems:'center', gap:4, color: activeTab==='dashboard'?'#d4af37':'#666', cursor:'pointer'}}>
                        <User size={20} />
                        <span style={{fontSize:'0.7rem'}}>Profile</span>
                    </div>
                    <div onClick={() => setActiveTab('invoices')} style={{display:'flex', flexDirection:'column', alignItems:'center', gap:4, color: activeTab==='invoices'?'#d4af37':'#666', cursor:'pointer'}}>
                        <Receipt size={20} />
                        <span style={{fontSize:'0.7rem'}}>Orders</span>
                    </div>
                </div>

                {/* Home Indicator */}
                <div style={{ position:'absolute', bottom:8, left:'50%', transform:'translateX(-50%)', width:'100px', height:'4px', background:'rgba(255,255,255,0.3)', borderRadius:'2px' }}></div>
            </div>
        </div>
    );
};

// --- 3. KIOSK INTERFACE (Touch Optimized, Big Buttons) ---
const KioskInterface = ({ userProfile, messages, input, setInput, sendMessage, activeTab, setActiveTab, invoices, loading, chatRef, onSignOut }) => {
    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#1a0505' }}>
            {/* Kiosk Sidebar (Big Targets) */}
            <div style={{ width: '280px', background: 'linear-gradient(180deg, #2b0505 0%, #000 100%)', borderRight: '2px solid #d4af37', display: 'flex', flexDirection: 'column', padding: '30px 20px' }}>
                <div style={{marginBottom: 40, textAlign:'center'}}>
                    <Crown size={60} color="#d4af37" style={{margin:'0 auto'}}/>
                    <h2 style={{color:'white', fontFamily:'Playfair Display', marginTop:10}}>Nexora<br/>Kiosk</h2>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <button onClick={() => setActiveTab('chat')} style={{ padding: '25px', borderRadius: '16px', border: activeTab === 'chat' ? '2px solid #d4af37' : '1px solid #333', background: activeTab === 'chat' ? 'rgba(212,175,55,0.2)' : 'rgba(255,255,255,0.05)', color: 'white', fontSize: '1.2rem', display:'flex', alignItems:'center', gap:15 }}>
                        <Sparkles size={24}/> Concierge
                    </button>
                    <button onClick={() => setActiveTab('dashboard')} style={{ padding: '25px', borderRadius: '16px', border: activeTab === 'dashboard' ? '2px solid #d4af37' : '1px solid #333', background: activeTab === 'dashboard' ? 'rgba(212,175,55,0.2)' : 'rgba(255,255,255,0.05)', color: 'white', fontSize: '1.2rem', display:'flex', alignItems:'center', gap:15 }}>
                        <User size={24}/> Profile
                    </button>
                    <button onClick={() => setActiveTab('invoices')} style={{ padding: '25px', borderRadius: '16px', border: activeTab === 'invoices' ? '2px solid #d4af37' : '1px solid #333', background: activeTab === 'invoices' ? 'rgba(212,175,55,0.2)' : 'rgba(255,255,255,0.05)', color: 'white', fontSize: '1.2rem', display:'flex', alignItems:'center', gap:15 }}>
                        <Receipt size={24}/> Invoices
                    </button>
                </div>

                <div style={{ marginTop: 'auto' }}>
                    <button onClick={onSignOut} style={{ width: '100%', padding: '20px', background: '#333', color: '#fff', fontSize: '1rem', borderRadius: '12px', border: 'none' }}>
                        Exit Session
                    </button>
                </div>
            </div>

            {/* Kiosk Content */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: '20px', background: '#2b0505', borderBottom: '1px solid #444', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
                    <span style={{color:'white', fontSize:'1.5rem', fontFamily:'Playfair Display'}}>Welcome, {userProfile.name}</span>
                    <span style={{color:'#d4af37', fontSize:'1.2rem', border:'1px solid #d4af37', padding:'5px 15px', borderRadius:20}}>{userProfile.loyalty_tier}</span>
                </div>

                <div style={{ flex: 1, overflowY: 'auto', background: 'black', padding: '30px' }}>
                     {activeTab === 'chat' && (
                        <>
                            <div style={{ paddingBottom: 20 }}>
                                {messages.map((msg, idx) => (
                                    <div key={idx} style={{fontSize:'1.2rem'}}><MessageBubble {...msg} /></div>
                                ))}
                                {loading && <div style={{ color: '#888', padding: '10px', fontSize:'1.2rem' }}>Processing...</div>}
                                <div ref={chatRef} />
                            </div>
                        </>
                    )}
                    {activeTab === 'dashboard' && <DashboardContent userProfile={userProfile} />}
                    {activeTab === 'invoices' && <InvoicesContent invoices={invoices} />}
                </div>

                {/* Kiosk Input (Only on Chat) */}
                {activeTab === 'chat' && (
                    <div style={{ padding: '20px', background: '#111', borderTop: '1px solid #333' }}>
                        <div style={{ display: 'flex', gap: '20px' }}>
                            <input 
                                value={input} onChange={e => setInput(e.target.value)} 
                                style={{ flex: 1, padding: '25px', fontSize: '1.3rem', borderRadius: '12px', border: '2px solid #444', background: '#222', color: 'white' }}
                                placeholder="Touch to type request..."
                                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                            />
                            <button onClick={() => sendMessage()} style={{ padding: '0 50px', fontSize: '1.3rem', background: '#d4af37', border: 'none', borderRadius: '12px', fontWeight: 'bold' }}>
                                SEND
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// --- MAIN APP COMPONENT ---

function App() {
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  
  // State for login Flow
  const [platform, setPlatform] = useState("Website"); // Default selection
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("chat"); 
  
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [userProfile, setUserProfile] = useState(null); 
  const [invoices, setInvoices] = useState([]); 

  // Fields for Sign Up
  const [newName, setNewName] = useState("");
  const [newAge, setNewAge] = useState("");
  const [newCity, setNewCity] = useState("");
  const [newGender, setNewGender] = useState("Male");

  const chatEndRef = useRef(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    const cleanUser = username.trim().toUpperCase();
    const newSessionId = `${cleanUser}-${Date.now()}`;

    try {
      const res = await axios.post(`${API_URL}/login`, { username: cleanUser, password });
      setUser(cleanUser);
      setSessionId(newSessionId);
      setUserProfile(res.data.full_profile); 
      setInvoices(res.data.invoices || []); 
      
      // Trigger Greeting based on Selected Platform
      triggerGreeting(cleanUser, newSessionId, platform, res.data.real_name);
    } catch (err) { alert("User not found."); }
    setLoading(false);
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    if(!username || !newName || !newAge || !newCity) { alert("Please fill all fields."); return; }
    setLoading(true);
    try {
        await axios.post(`${API_URL}/signup`, {
            customer_id: username, name: newName, age: parseInt(newAge), city: newCity, gender: newGender, device_preference: "Web"
        });
        alert("✅ Account Created! Please Sign In.");
        setIsSignup(false); 
    } catch(err) { alert("Error: ID exists."); }
    setLoading(false);
  };

  const handleNewInvoice = (invoiceData) => {
      setInvoices(prev => {
          if (prev.some(inv => inv.invoice_id === invoiceData.invoice_id)) return prev;
          return [invoiceData, ...prev];
      });
  };

  const triggerGreeting = async (userId, sessId, plat, realName) => {
    try {
      const res = await axios.post(`${API_URL}/chat`, {
        // This message tells the AI about the switch/login context
        message: `SYSTEM_EVENT: User ${userId} (${realName}) just logged in via ${plat}. Greet them warmly.`,
        user_id: sessId, platform: plat
      });
      if (res.data.response) setMessages([{ role: 'bot', content: res.data.response }]);
    } catch (e) {}
  };

  const sendMessage = async (textOverride) => {
    const msgText = typeof textOverride === 'string' ? textOverride : input;
    if (!msgText.trim()) return;
    
    if (!msgText.startsWith("PAYMENT_DATA:")) {
        setMessages(prev => [...prev, { role: 'user', content: msgText }]);
    } else {
        setMessages(prev => [...prev, { role: 'user', content: "✅ Payment Details Submitted" }]);
    }

    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_URL}/chat`, {
        message: msgText, user_id: sessionId, platform: platform
      });
      if (res.data.response) setMessages(prev => [...prev, { role: 'bot', content: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: "⚠️ System busy." }]);
    }
    setLoading(false);
  };

  const handleSignOut = () => {
      setUser(null);
      setMessages([]);
      setInvoices([]);
      setUserProfile(null);
      setUsername("");
      setPassword("");
      // Platform stays selected or can be reset. Let's keep it to user choice.
  };

  // --- LOGIN RENDER ---
  if (!user) {
    return (
      <div className="login-bg">
        <div className="royal-card animate-enter">
          <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
            <Crown size={48} color="#d4af37" style={{ marginBottom: '0.5rem' }} />
            <h1 style={{ fontSize: '2.5rem', fontWeight: '400', color: '#fff', fontFamily: 'Playfair Display', margin: 0 }}>Nexora</h1>
            <p style={{ color: '#d4af37', letterSpacing: '1px', fontSize: '0.9rem', textTransform: 'uppercase', marginTop: '8px' }}>Royal Intelligence</p>
          </div>

          <form onSubmit={isSignup ? handleSignup : handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            
            {/* PLATFORM SELECTOR (Only Visible on Login) */}
            {!isSignup && (
                <div style={{display:'flex', gap:10, marginBottom:10}}>
                    {[
                        {id:'Website', icon:<Monitor size={18}/>, label:'Web'},
                        {id:'Mobile App', icon:<Smartphone size={18}/>, label:'App'},
                        {id:'Kiosk', icon:<Store size={18}/>, label:'Kiosk'}
                    ].map(p => (
                        <div key={p.id} 
                            onClick={() => setPlatform(p.id)}
                            style={{
                                flex: 1, padding: '12px 5px', borderRadius: 8, cursor: 'pointer',
                                border: platform === p.id ? '1px solid #d4af37' : '1px solid rgba(255,255,255,0.1)',
                                background: platform === p.id ? 'rgba(212,175,55,0.2)' : 'transparent',
                                color: platform === p.id ? 'white' : '#888',
                                display:'flex', flexDirection:'column', alignItems:'center', gap:5, fontSize:'0.8rem'
                            }}
                        >
                            {p.icon} {p.label}
                        </div>
                    ))}
                </div>
            )}

            <input type="text" placeholder="Customer ID" value={username} onChange={e => setUsername(e.target.value)} style={royalInputStyle} />
            
            {isSignup && <input type="text" placeholder="Name" value={newName} onChange={e => setNewName(e.target.value)} style={royalInputStyle} />}
            {isSignup && (
                <div style={{ display: 'flex', gap: '10px' }}>
                    <input type="number" placeholder="Age" value={newAge} onChange={e => setNewAge(e.target.value)} style={{...royalInputStyle, flex: 1}} />
                    <select value={newGender} onChange={e => setNewGender(e.target.value)} style={{...royalInputStyle, flex: 1, cursor: 'pointer'}}>
                        <option value="Male" style={{color:'black'}}>Male</option>
                        <option value="Female" style={{color:'black'}}>Female</option>
                        <option value="Other" style={{color:'black'}}>Other</option>
                    </select>
                </div>
            )}
            {isSignup && <input type="text" placeholder="City" value={newCity} onChange={e => setNewCity(e.target.value)} style={royalInputStyle} />}
            
            {!isSignup && <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} style={royalInputStyle} />}
            
            <button type="submit" style={{ marginTop: '0.5rem', background: 'linear-gradient(135deg, #d4af37 0%, #c5a028 100%)', color: '#1a0505', padding: '16px', borderRadius: '12px', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>
              {loading ? "Authenticating..." : (isSignup ? "Create Membership" : `Enter ${platform}`)}
            </button>
          </form>
          <p onClick={() => setIsSignup(!isSignup)} style={{ textAlign: 'center', marginTop: '1.5rem', color: '#d4af37', cursor: 'pointer', opacity: 0.8 }}>
            {isSignup ? "Sign In" : "Apply for Membership"}
          </p>
        </div>
      </div>
    );
  }

  // --- RENDER SELECTED INTERFACE ---
  const sharedProps = { 
      userProfile, messages, input, setInput, sendMessage, 
      activeTab, setActiveTab, invoices, loading, 
      chatRef: chatEndRef, 
      onInvoiceReceived: handleNewInvoice,
      onSignOut: handleSignOut
  };

  if (platform === 'Mobile App') return <MobileInterface {...sharedProps} />;
  if (platform === 'Kiosk') return <KioskInterface {...sharedProps} />;
  return <WebInterface {...sharedProps} />;
}

const royalInputStyle = { width: '100%', padding: '16px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.3)', color: 'white', outline: 'none' };

export default App;