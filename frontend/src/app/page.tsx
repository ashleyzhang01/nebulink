"use client";
import { useState, useEffect } from 'react';
import SearchBox from '@/components/SearchBox';
import dynamic from 'next/dynamic';

const NetworkGraph = dynamic(() => import('../components/NetworkGraph'), {
  ssr: false,
  loading: () => <p>Loading...</p>
});

const PublicNetworkGraph = dynamic(() => import('../components/PublicNetworkGraph'), {
  ssr: false,
  loading: () => <p>Loading public network...</p>
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
          <div style={{ 
            position: 'absolute', 
            top: '70px', 
            left: '50%', 
            transform: 'translateX(-50%)', 
            zIndex: 10 
          }}>
            <SearchBox />
          </div>

          {/* NetworkGraph */}
          <NetworkGraph />
        </div>
      ) : (
        <PublicNetworkGraph />
      )}
    </div>
  );
}
