import { AppProvider } from './contexts/AppContext';
import { Dashboard } from './components/Dashboard';

function App() {
  return (
    <AppProvider>
      <Dashboard />
    </AppProvider>
  );
}

export default App;