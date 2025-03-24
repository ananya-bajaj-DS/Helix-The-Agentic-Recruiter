// import { useState, useEffect } from 'react';
// import axios from 'axios';
// import io from 'socket.io-client';
// import './App.css';

// // Connect to the Flask backend's Socket.IO server
// const socket = io('http://localhost:5000', { transports: ['websocket'] });

// // Log Socket.IO connection status
// socket.on('connect', () => {
//   console.log('Socket.IO connected successfully');
// });
// socket.on('connect_error', (error) => {
//   console.error('Socket.IO connection error:', error);
// });

// const App: React.FC = () => {
//   const [messages, setMessages] = useState<string[]>([]);
//   const [input, setInput] = useState('');
//   const [sequence, setSequence] = useState<string[]>([]);
//   const userId = '123';

//   useEffect(() => {
//     socket.on('sequence_updated', (data: { sequence: string }) => {
//       console.log('Socket.IO sequence_updated received:', data);
//       setSequence(data.sequence.split('\n'));
//     });
//     return () => {
//       socket.off('sequence_updated');
//     };
//   }, []);

//   const sendMessage = async () => {
//     if (input.trim() === '') return;
//     setMessages([...messages, `You: ${input}`]);

//     try {
//       const response = await axios.post(
//         '/api/chat',
//         { user_id: userId, message: input, history: [] },
//         { withCredentials: true }
//       );
//       setMessages((prev) => [...prev, `AI: ${response.data.response}`]);

//       const sequenceResponse = await axios.post(
//         '/api/sequence',
//         { user_id: userId, preferences: input },
//         { withCredentials: true }
//       );
//       setSequence(sequenceResponse.data.sequence.split('\n'));
//     } catch (error: any) {
//       const errorMessage = error.response?.data?.error || error.message || 'Unknown error';
//       setMessages((prev) => [...prev, `AI: Error - ${errorMessage}`]);
//     }

//     setInput('');
//   };

//   const updateSequence = async (updatedSequence: string[]) => {
//     const sequenceText = updatedSequence.join('\n');
//     setSequence(updatedSequence);

//     try {
//       await axios.post(
//         '/api/update_sequence',
//         { user_id: userId, sequence: sequenceText },
//         { withCredentials: true }
//       );
//       socket.emit('update_sequence', { sequence: sequenceText });
//     } catch (error: any) {
//       console.error('updateSequence: Error occurred:', error);
//     }
//   };

//   return (
//     <div className="app">
//       <div className="chat-bar">
//         <h2>Chat</h2>
//         <div className="messages">
//           {messages.map((msg, index) => (
//             <div key={index} className="message">{msg}</div>
//           ))}
//         </div>
//         <div className="input-container">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             onKeyPress={(e) => { if (e.key === 'Enter') sendMessage(); }}
//             placeholder="Type your message..."
//           />
//           <button onClick={sendMessage}>Send</button>
//         </div>
//       </div>
//       <div className="workspace">
//         <h2>Outreach Sequence</h2>
//         <div className="sequence">
//           {sequence.map((line, index) => (
//             <textarea
//               key={index}
//               value={line}
//               onChange={(e) => {
//                 const newSequence = [...sequence];
//                 newSequence[index] = e.target.value;
//                 updateSequence(newSequence);
//               }}
//               rows={3}
//             />
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// };

// export default App;



//  test code
import { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import './App.css';

// Connect to Flask backend (port 5000 assumed to be reverse-proxied by NGINX)
const socket = io('http://localhost:5000', { transports: ['websocket'] });

const App: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState('');
  const [sequence, setSequence] = useState<string[]>([]);
  const userId = '123';

  useEffect(() => {
    // Listen for real-time sequence updates
    socket.on('sequence_updated', (data: { sequence: string }) => {
      setSequence(data.sequence.split('\n'));
    });

    return () => {
      socket.off('sequence_updated');
    };
  }, []);

  const sendMessage = async () => {
    if (input.trim() === '') return;
    setMessages([...messages, `You: ${input}`]);

    try {
      // Call /api/chat
      const response = await axios.post('/api/chat', {
        user_id: userId,
        message: input,
        history: []
      });
      setMessages((prev) => [...prev, `AI: ${response.data.response}`]);

      // Call /api/sequence
      const sequenceResponse = await axios.post('/api/sequence', {
        user_id: userId,
        preferences: input
      });
      setSequence(sequenceResponse.data.sequence.split('\n'));
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || error.message || 'Unknown error';
      setMessages((prev) => [...prev, `AI: Error - ${errorMessage}`]);
    }

    setInput('');
  };

  const updateSequence = async (updatedSequence: string[]) => {
    const sequenceText = updatedSequence.join('\n');
    setSequence(updatedSequence);

    try {
      await axios.post('/api/update_sequence', {
        user_id: userId,
        sequence: sequenceText
      });

      socket.emit('update_sequence', { sequence: sequenceText });
    } catch (error) {
      console.error('Error updating sequence:', error);
    }
  };

  return (
    <div className="app">
      <div className="chat-bar">
        <h2>Chat</h2>
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className="message">{msg}</div>
          ))}
        </div>
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => { if (e.key === 'Enter') sendMessage(); }}
            placeholder="Type your message..."
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>

      <div className="workspace">
        <h2>Outreach Sequence</h2>
        <div className="sequence">
          {sequence.map((line, index) => (
            <textarea
              key={index}
              value={line}
              onChange={(e) => {
                const newSequence = [...sequence];
                newSequence[index] = e.target.value;
                updateSequence(newSequence);
              }}
              rows={3}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default App;
