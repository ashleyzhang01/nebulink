import OriginalGraph from '../components/OriginalGraph';
import SearchBox from '@/components/SearchBox';

export default function Home() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
    <SearchBox />
    <OriginalGraph />
  </div>
  );
}
