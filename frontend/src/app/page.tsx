'use client';
import { useState, useEffect, useCallback } from 'react';
import { api, ClipboardEntry } from '@/lib/api';
import { ClipboardCard } from '@/components/ClipboardCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'sonner';
import { Search, LayoutDashboard, Link, Code, Database, FileJson, Key, Star } from 'lucide-react';

const FILTERS = [
  { name: 'All', icon: LayoutDashboard },
  { name: 'URL', icon: Link },
  { name: 'Code', icon: Code },
  { name: 'SQL', icon: Database },
  { name: 'JSON', icon: FileJson },
  { name: 'Secrets', icon: Key },
  { name: 'Favorites', icon: Star },
];

export default function Home() {
  const [entries, setEntries] = useState<ClipboardEntry[]>([]);
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  const fetchEntries = useCallback(async () => {
    try {
      const is_pinned = activeFilter === 'Favorites' ? true : undefined;
      let content_type = undefined;
      
      if (activeFilter !== 'All' && activeFilter !== 'Favorites') {
        content_type = activeFilter;
      }

      const data = await api.getHistory({ search, content_type, is_pinned });
      setEntries(data);
    } catch (err) {
      console.error(err);
      // Optional: uncomment below to show toast on fetch error (might be noisy)
      // toast.error('Failed to fetch clipboard history');
    } finally {
      setLoading(false);
    }
  }, [search, activeFilter]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchEntries();
    
    // Poll for new entries every 2s in foreground
    const interval = setInterval(fetchEntries, 2000);
    return () => clearInterval(interval);
  }, [fetchEntries]);

  const handleCopy = () => {
    toast.success('Copied to clipboard');
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteEntry(id);
      setEntries(entries.filter(e => e.id !== id));
      toast.success('Entry deleted');
    } catch {
      toast.error('Failed to delete entry');
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear history? (Pinned items will be kept)')) return;
    try {
      await api.clearHistory();
      fetchEntries();
      toast.success('History cleared');
    } catch {
      toast.error('Failed to clear history');
    }
  };

  const handleTogglePin = async (id: string) => {
    try {
      const updated = await api.togglePin(id);
      setEntries(entries.map(e => e.id === id ? updated : e));
    } catch {
      toast.error('Failed to toggle pin');
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <div className="w-64 border-r border-border bg-muted/10 p-4 flex flex-col gap-2">
        <div className="font-bold text-xl mb-4 tracking-tight flex items-center gap-2 px-2 pt-2">
          <div className="w-8 h-8 rounded bg-primary flex items-center justify-center text-primary-foreground shadow-sm">
            <LayoutDashboard size={18} />
          </div>
          PasteLens
        </div>
        
        <div className="flex flex-col gap-1 mt-4">
          {FILTERS.map((f) => {
            const Icon = f.icon;
            return (
              <Button
                key={f.name}
                variant={activeFilter === f.name ? 'secondary' : 'ghost'}
                className="justify-start gap-3 w-full"
                onClick={() => setActiveFilter(f.name)}
              >
                <Icon size={16} />
                {f.name}
              </Button>
            );
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <div className="h-16 border-b border-border flex items-center px-6 gap-4 bg-background/95 backdrop-blur z-10">
          <div className="relative flex-1 max-w-xl">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input 
              placeholder="Search clipboard history..." 
              className="pl-9 bg-muted/50 border-none focus-visible:ring-1 shadow-inner"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex-1" />
          <Button variant="outline" onClick={handleClearHistory} className="text-muted-foreground">
            Clear History
          </Button>
        </div>

        {/* Feed */}
        <ScrollArea className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-8 pb-20">
            {loading && entries.length === 0 ? (
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="flex flex-col gap-2 p-4 border border-border rounded-xl bg-card">
                    <div className="flex justify-between">
                      <Skeleton className="h-6 w-20" />
                      <div className="flex gap-2">
                        <Skeleton className="h-8 w-8 rounded-md" />
                        <Skeleton className="h-8 w-8 rounded-md" />
                        <Skeleton className="h-8 w-8 rounded-md" />
                      </div>
                    </div>
                    <Skeleton className="h-24 w-full mt-2" />
                  </div>
                ))}
              </div>
            ) : entries.length === 0 ? (
              <div className="text-center text-muted-foreground py-20">No clipboard history found</div>
            ) : (
              (() => {
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                const yesterday = new Date(today);
                yesterday.setDate(yesterday.getDate() - 1);
                
                const grouped = {
                  Today: entries.filter(e => new Date(e.created_at) >= today),
                  Yesterday: entries.filter(e => new Date(e.created_at) >= yesterday && new Date(e.created_at) < today),
                  Older: entries.filter(e => new Date(e.created_at) < yesterday),
                };
                
                return Object.entries(grouped).map(([group, groupEntries]) => {
                  if (groupEntries.length === 0) return null;
                  return (
                    <div key={group} className="space-y-4">
                      <h3 className="text-sm font-medium text-muted-foreground tracking-widest uppercase">{group}</h3>
                      {groupEntries.map((entry) => (
                        <ClipboardCard
                          key={entry.id}
                          entry={entry}
                          onCopy={handleCopy}
                          onDelete={handleDelete}
                          onTogglePin={handleTogglePin}
                        />
                      ))}
                    </div>
                  );
                });
              })()
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
