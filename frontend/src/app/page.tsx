"use client";
import { useState, useEffect } from 'react';
import SearchBox from '@/components/SearchBox';
import dynamic from 'next/dynamic';

const NetworkGraph = dynamic(() => import('../components/NetworkGraph'), {
  ssr: false,
  loading: () => <p>Loading...</p>
});

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      {isLoggedIn ? (
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
          {/* Overlayed SearchBox */}
          <div style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 10 }}>
            <SearchBox />
          </div>

          {/* NetworkGraph */}
          <NetworkGraph />
        </div>
      ) : (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '100%',
          fontSize: '1.5rem',
          color: '#333'
        }}>
          Please log in to view the network graph.
        </div>
      )}
    </div>
  );
}
