import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { QRCodeSVG } from 'qrcode.react';
import { Smartphone, Monitor, Store, Send, User, ShoppingBag, Sparkles, Package, CreditCard, MapPin, Search, ArrowRight, Crown, Lock, FileText, Download, Receipt } from 'lucide-react';

const API_URL = "http://127.0.0.1:8000"; 

// --- COMPONENTS ---

const InvoiceCard = ({ data }) => {
    const inv = typeof data === 'string' ? JSON.parse(data) : data;
    return (
        <div className="animate-enter" style={{ background: 'white', color: '#1a0505', padding: '24px', borderRadius: '16px', width: '300px', border: '1px solid #e2e8f0', boxShadow: '0 4px 20px rgba(0,0,0,0.05)', position: 'relative' }}>
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

// --- UPDATED NavButton (Supports 'disabled') ---
const NavButton = ({ active, icon, label, onClick, disabled }) => (
  <div 
    onClick={disabled ? null : onClick} 
    className={`nav-item ${active ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
  >
    {icon} {label}
  </div>
);

const BotAvatar = ({ role }) => (
    role === 'bot' ? 
    <div style={{ width: '36px', height: '36px', background: 'rgba(255,255,255,0.1)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, border: '1px solid rgba(212, 175, 55, 0.2)' }}>
        <Sparkles size={18} color="#d4af37" />
    </div> : null
);

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

const MessageBubble = ({ role, content, onPay, onInvoiceReceived }) => {
    if (content.includes("||INVOICE_DATA:")) {
        const jsonStr = content.split("||INVOICE_DATA:")[1].split("||")[0];
        const cleanText = content.replace(/\|\|INVOICE_DATA:.*?\|\|/, "").trim();
        useEffect(() => { if (onInvoiceReceived) onInvoiceReceived(JSON.parse(jsonStr)); }, []);
        return (
            <div className={`msg-row animate-enter ${role}`}>
                <BotAvatar role={role} />
                <div className={`bubble ${role}`}>
                    <p style={{margin:0, marginBottom:'10px'}}>{cleanText}</p>
                    <InvoiceCard data={jsonStr} />
                </div>
            </div>
        );
    }
    if (content.includes("||QR_CODE:")) {
        const amount = content.split("||QR_CODE:")[1].split("||")[0].trim();
        const cleanText = content.replace(/\|\|QR_CODE:.*?\|\|/, "").trim();
        return (
            <div className={`msg-row animate-enter ${role}`}>
                <BotAvatar role={role} />
                <div className={`bubble ${role}`}>
                    <p style={{margin:0, marginBottom:'10px'}}>{cleanText}</p>
                    <div style={{ background: 'white', padding: '15px', borderRadius: '12px', display: 'inline-block' }}>
                        <QRCodeSVG value={`upi://pay?pa=nexora@upi&pn=Nexora&am=${amount}`} size={140} />
                        <p style={{ textAlign: 'center', color: '#000', margin: '5px 0 0', fontWeight: 'bold', fontSize: '0.9rem' }}>₹{amount}</p>
                    </div>
                </div>
            </div>
        );
    }
    if (content.includes("||CC_FORM||")) {
        const cleanText = content.replace("||CC_FORM||", "").trim();
        return (
            <div className={`msg-row animate-enter ${role}`}>
                <BotAvatar role={role} />
                <div className={`bubble ${role}`}>
                    <p style={{margin:0}}>{cleanText}</p>
                    <CCPaymentForm onPay={onPay} />
                </div>
            </div>
        );
    }
    return (
        <div className={`msg-row animate-enter ${role}`}>
            <BotAvatar role={role} />
            <div className={`bubble ${role}`}>
                {content.split('\n').map((line, i) => <p key={i} style={{ margin: 0 }}>{line}</p>)}
            </div>
        </div>
    );
};

// --- MAIN APP ---

function App() {
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [platform, setPlatform] = useState("Website");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("chat"); 
  
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [userProfile, setUserProfile] = useState(null); 
  const [invoices, setInvoices] = useState([]); 

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

  const handleSwitchPlatform = (newPlatform) => {
    if (newPlatform === platform) return;
    setPlatform(newPlatform);
    axios.post(`${API_URL}/chat`, {
      message: `SYSTEM_NOTE: User switched device to ${newPlatform}.`,
      user_id: sessionId, platform: newPlatform
    });
  };

  // --- RENDER VIEWS ---

  const renderDashboard = () => (
    <div className="dashboard-container animate-enter">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2 style={{ fontSize: '2.5rem', fontFamily: 'Playfair Display', margin: 0, color: '#e1adac' }}>Dashboard</h2>
        <div style={{ padding: '6px 16px', border: '1px solid rgba(212,175,55,0.4)', borderRadius: '20px', color: '#d4af37', fontSize: '0.85rem', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '1px' }}>
          {userProfile.loyalty_tier} Member
        </div>
      </div>
      
      <div className="profile-hero">
        <div className="avatar-large">{userProfile.name[0]}</div>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '2.5rem', margin: 0, fontWeight: '700', lineHeight: '1.2', color: 'white', fontFamily: 'Playfair Display' }}>{userProfile.name}</h3>
          <div style={{ display: 'flex', gap: '20px', marginTop: '16px', color: '#a3a3a3' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><User size={16} color="#d4af37"/> {userProfile.customer_id}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><MapPin size={16} color="#d4af37"/> {userProfile.city}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Smartphone size={16} color="#d4af37"/> {userProfile.device_preference}</span>
          </div>
        </div>
      </div>

      <h3 style={{ margin: '40px 0 20px', color: '#d4af37', fontSize: '0.9rem', letterSpacing: '2px', fontWeight: '700' }}>RECENT ORDERS</h3>
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

  const renderInvoices = () => (
    <div className="dashboard-container animate-enter">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
            <h2 style={{ fontSize: '2.5rem', fontFamily: 'Playfair Display', margin: 0, color: '#e1adac' }}>Invoices</h2>
        </div>
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

  // --- LOGIN ---
  if (!user) {
    return (
      <div className="login-bg">
        <div className="royal-card animate-enter">
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <Crown size={48} color="#d4af37" style={{ marginBottom: '1rem' }} />
            <h1 style={{ fontSize: '2.5rem', fontWeight: '400', color: '#fff', fontFamily: 'Playfair Display', margin: 0 }}>Nexora</h1>
            <p style={{ color: '#d4af37', letterSpacing: '1px', fontSize: '0.9rem', textTransform: 'uppercase', marginTop: '8px' }}>Royal Intelligence</p>
          </div>
          <form onSubmit={isSignup ? handleSignup : handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
            <input type="text" placeholder="Customer ID" value={username} onChange={e => setUsername(e.target.value)} style={royalInputStyle} />
            {isSignup && <input type="text" placeholder="Name" value={newName} onChange={e => setNewName(e.target.value)} style={royalInputStyle} />}
            {isSignup && <input type="text" placeholder="City" value={newCity} onChange={e => setNewCity(e.target.value)} style={royalInputStyle} />}
            {!isSignup && <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} style={royalInputStyle} />}
            <button type="submit" style={{ marginTop: '1rem', background: 'linear-gradient(135deg, #d4af37 0%, #c5a028 100%)', color: '#1a0505', padding: '16px', borderRadius: '12px', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>
              {loading ? "Authenticating..." : (isSignup ? "Create Membership" : "Enter Concierge")}
            </button>
          </form>
          <p onClick={() => setIsSignup(!isSignup)} style={{ textAlign: 'center', marginTop: '1.5rem', color: '#d4af37', cursor: 'pointer', opacity: 0.8 }}>
            {isSignup ? "Sign In" : "Apply for Membership"}
          </p>
        </div>
      </div>
    );
  }

  // --- MAIN LAYOUT ---
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div className="sidebar">
        <div style={{ marginBottom: '50px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Crown size={24} color="#d4af37" />
          <span style={{ fontFamily: 'Playfair Display', fontSize: '1.4rem', color: 'white' }}>Nexora</span>
        </div>
        
        <NavButton active={activeTab === 'chat'} icon={<Sparkles size={18} />} label="Concierge" onClick={() => setActiveTab('chat')} />
        <NavButton active={activeTab === 'dashboard'} icon={<User size={18} />} label="Dashboard" onClick={() => setActiveTab('dashboard')} />
        <NavButton active={activeTab === 'invoices'} icon={<Receipt size={18} />} label="Invoices" onClick={() => setActiveTab('invoices')} />
        
        <div style={{ height: '30px' }} />
        <p style={{ fontSize: '0.7rem', color: '#666', fontWeight: 'bold', paddingLeft: '18px', marginBottom: '10px' }}>CHANNEL</p>
        
        {/* Buttons are disabled unless in chat mode */}
        <NavButton active={platform === 'Website'} icon={<Monitor size={18} />} label="Website" onClick={() => handleSwitchPlatform('Website')} disabled={activeTab !== 'chat'} />
        <NavButton active={platform === 'Mobile App'} icon={<Smartphone size={18} />} label="Mobile App" onClick={() => handleSwitchPlatform('Mobile App')} disabled={activeTab !== 'chat'} />
        <NavButton active={platform === 'Kiosk'} icon={<Store size={18} />} label="Kiosk" onClick={() => handleSwitchPlatform('Kiosk')} disabled={activeTab !== 'chat'} />

        <div style={{ marginTop: 'auto', background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '16px' }}>
            <p style={{fontWeight:'bold', color: 'white'}}>{userProfile?.name}</p>
            <p style={{fontSize:'0.8rem', color: '#888'}}>{userProfile?.loyalty_tier}</p>
            <button onClick={() => window.location.reload()} style={{ width: '100%', marginTop: '10px', padding: '8px', background: 'transparent', border: '1px solid #333', color: '#888', borderRadius: '8px', cursor: 'pointer' }}>Sign Out</button>
        </div>
      </div>

      <div className="chat-layout">
        <div style={{ padding: '24px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontFamily: 'Playfair Display', fontSize: '1.5rem', color: 'white' }}>
            {activeTab === 'chat' ? `${platform} Concierge` : (activeTab === 'dashboard' ? 'Dashboard' : 'My Invoices')}
          </h2>
        </div>

        {activeTab === 'chat' && (
          <>
            <div className="messages-container">
              {messages.map((msg, idx) => (
                <MessageBubble key={idx} role={msg.role} content={msg.content} onPay={sendMessage} onInvoiceReceived={handleNewInvoice} />
              ))}
              {loading && <div style={{ color: '#666', padding: '0 20px' }}>Nexora is thinking...</div>}
              <div ref={chatEndRef} />
            </div>
            <div className="input-zone">
              <div className="input-bar">
                <input className="input-field" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} placeholder="Ask Nexora..." />
                <button onClick={() => sendMessage()} className="send-fab"><ArrowRight size={20} /></button>
              </div>
            </div>
          </>
        )}

        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'invoices' && renderInvoices()}

      </div>
    </div>
  );
}

const royalInputStyle = { width: '100%', padding: '16px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.3)', color: 'white', outline: 'none' };

export default App;