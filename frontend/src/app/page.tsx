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
      {/* <SearchBox /> */}
      {isLoggedIn ? <NetworkGraph /> : <PublicNetworkGraph />}
    </div>
  );
}