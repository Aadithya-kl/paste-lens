'use client';
import { useState } from 'react';
import { ClipboardEntry } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Copy, Trash2, Eye, EyeOff, Pin } from 'lucide-react';

interface ClipboardCardProps {
  entry: ClipboardEntry;
  onCopy: () => void;
  onDelete: (id: string) => void;
  onTogglePin: (id: string) => void;
}

export function ClipboardCard({ entry, onCopy, onDelete, onTogglePin }: ClipboardCardProps) {
  const [revealed, setRevealed] = useState(!entry.is_sensitive);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(entry.content);
    onCopy();
  };
  
  return (
    <Card className={`p-4 flex flex-col gap-2 transition-all duration-200 hover:-translate-y-[2px] hover:shadow-md hover:bg-muted/50 ${entry.is_pinned ? 'border-primary/50' : 'border-border'}`}>
      <div className="flex justify-between items-start">
        <div className="flex gap-2 items-center">
          <Badge variant={entry.is_sensitive ? "destructive" : "secondary"}>
            {entry.content_type}
          </Badge>
          {entry.copy_count > 1 && (
            <Badge variant="outline" className="text-xs">
              Copied {entry.copy_count}x
            </Badge>
          )}
        </div>
        <div className="flex gap-1">
          <Button variant="ghost" size="icon" onClick={() => onTogglePin(entry.id)} className="h-8 w-8">
            {entry.is_pinned ? <Pin className="h-4 w-4 fill-current" /> : <Pin className="h-4 w-4" />}
          </Button>
          {entry.is_sensitive && (
            <Button variant="ghost" size="icon" onClick={() => setRevealed(!revealed)} className="h-8 w-8">
              {revealed ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          )}
          <Button variant="ghost" size="icon" onClick={handleCopy} className="h-8 w-8">
            <Copy className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => onDelete(entry.id)} className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <div className="mt-2 bg-muted/30 p-3 rounded-md font-mono text-sm max-h-40 overflow-hidden relative">
        {revealed ? (
          <pre className="whitespace-pre-wrap break-all">{entry.content}</pre>
        ) : (
          <div className="flex items-center h-8 text-muted-foreground tracking-widest text-lg">
            ••••••••••••••••••••••••
          </div>
        )}
        {revealed && entry.content.length > 200 && (
          <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-background to-transparent" />
        )}
      </div>
      
      <div className="text-xs text-muted-foreground mt-1 text-right">
        {new Date(entry.created_at).toLocaleString()}
      </div>
    </Card>
  );
}
