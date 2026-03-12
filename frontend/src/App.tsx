import { useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { useCalls } from './hooks/useCalls';
import { useCallStore } from './store/callStore';
import './App.css';

// Import components
import { CallButton } from './components/CallButton';
import { CallStatus } from './components/CallStatus';
import { CallHistory } from './components/CallHistory';
import { IncomingCall } from './components/IncomingCall';

function App() {
  useWebSocket();
  const { fetchCallHistory } = useCalls();
  const { wsConnected, error, activeCall, incomingCall } = useCallStore();

  useEffect(() => {
    // Fetch initial call history
    fetchCallHistory();
  }, [fetchCallHistory]);

  return (
    <div className="app">
      <header className="header">
        <h1>Twilio Voice Caller</h1>
        <p className="header-subtitle">Make and receive calls with real-time updates</p>
        <div className="connection-status">
          <span className={`status-indicator ${wsConnected ? '' : 'disconnected'}`}></span>
          <span>{wsConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="container">
          <h2 className="section-title">Make a Call</h2>
          <CallButton />
        </div>

        {activeCall && (
          <div className="container">
            <h2 className="section-title">Active Call</h2>
            <CallStatus call={activeCall} />
          </div>
        )}

        {incomingCall && (
          <IncomingCall call={incomingCall} />
        )}

        <div className="container">
          <h2 className="section-title">Call History</h2>
          <CallHistory />
        </div>
      </main>
    </div>
  );
}

export default App;
