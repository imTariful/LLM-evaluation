import { useState } from 'react';
import { LayoutDashboard, List, Terminal, Activity, Layers, Zap, Trophy, TrendingUp } from 'lucide-react';
import { Dashboard } from './components/Dashboard';
import { TraceViewer } from './components/TraceLog';
import { TestRunner } from './components/TestRunner';
import { Leaderboard } from './components/Leaderboard';
import { DriftAnalysis } from './components/DriftAnalysis';

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard': return <Dashboard />;
            case 'traces': return <TraceViewer />;
            case 'leaderboard': return <Leaderboard />;
            case 'drift': return <DriftAnalysis />;
            case 'test': return <TestRunner />;
            default: return <div className="p-10 text-center text-gray-500">Coming Soon</div>;
        }
    };

    return (
        <div className="min-h-screen bg-[#0f1117] text-gray-100 flex">
            {/* SIDEBAR */}
            <aside className="w-64 border-r border-gray-800 bg-[#161b22] flex flex-col">
                <div className="p-6 border-b border-gray-800">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <span className="font-bold text-white">E</span>
                        </div>
                        <span className="font-bold text-lg tracking-tight">EvalPlatform</span>
                    </div>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    <NavItem
                        icon={LayoutDashboard}
                        label="Overview"
                        active={activeTab === 'dashboard'}
                        onClick={() => setActiveTab('dashboard')}
                    />
                    <NavItem
                        icon={Trophy}
                        label="Leaderboard"
                        active={activeTab === 'leaderboard'}
                        onClick={() => setActiveTab('leaderboard')}
                    />
                    <NavItem
                        icon={TrendingUp}
                        label="Drift Analysis"
                        active={activeTab === 'drift'}
                        onClick={() => setActiveTab('drift')}
                    />
                    <NavItem
                        icon={List}
                        label="Traces & Logs"
                        active={activeTab === 'traces'}
                        onClick={() => setActiveTab('traces')}
                    />
                    <NavItem
                        icon={Zap}
                        label="Test Runner"
                        active={activeTab === 'test'}
                        onClick={() => setActiveTab('test')}
                    />
                    <NavItem
                        icon={Terminal}
                        label="Prompt Manager"
                        active={activeTab === 'prompts'}
                        onClick={() => setActiveTab('prompts')}
                    />
                    <div className="pt-4 pb-2 px-3 text-xs font-bold text-gray-500 uppercase tracking-wider">
                        Configuration
                    </div>
                    <NavItem
                        icon={Layers}
                        label="Datasets"
                        onClick={() => { }}
                    />
                </nav>

                <div className="p-4 border-t border-gray-800">
                    <div className="flex items-center gap-3 px-3 py-2 bg-gray-800/50 rounded-lg">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-xs text-gray-400 font-mono">System Online</span>
                    </div>
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main className="flex-1 overflow-auto bg-[#0f1117]">
                <header className="h-16 border-b border-gray-800 flex items-center justify-between px-8 bg-[#161b22]/50 backdrop-blur-md sticky top-0 z-10">
                    <h1 className="text-lg font-semibold text-white capitalize">{activeTab}</h1>
                    <div className="flex items-center gap-4">
                        <button 
                            onClick={() => setActiveTab('test')}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                        >
                            + New Test
                        </button>
                    </div>
                </header>

                <div className="p-8 max-w-7xl mx-auto">
                    {renderContent()}
                </div>
            </main>
        </div>
    );
}

function NavItem({ icon: Icon, label, active, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${active
                    ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
        >
            <Icon size={18} />
            {label}
        </button>
    );
}

export default App;
