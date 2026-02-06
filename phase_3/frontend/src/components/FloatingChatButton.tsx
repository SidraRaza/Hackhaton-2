'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X } from 'lucide-react';
import { Button } from './ui/button';

interface FloatingChatButtonProps {
  isOpen: boolean;
  onToggle: () => void;
}

export const FloatingChatButton: React.FC<FloatingChatButtonProps> = ({ isOpen, onToggle }) => {
  return (
    <motion.div
      className="fixed bottom-6 right-6 z-50"
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ delay: 0.5, type: 'spring', stiffness: 200, damping: 15 }}
    >
      <AnimatePresence>
        {isOpen ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-16 right-0 mb-2"
          >
            <div className="bg-background border border-border rounded-lg shadow-lg p-4 w-80">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold text-foreground">AI Assistant</h3>
                <Button variant="ghost" size="sm" onClick={onToggle} className="p-1 h-auto">
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="text-sm text-muted-foreground">
                How can I help you today?
              </div>
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>

      <Button
        size="lg"
        className={`h-14 w-14 rounded-full shadow-lg ${
          isOpen ? 'bg-destructive hover:bg-destructive/90' : 'bg-primary hover:bg-primary/90'
        }`}
        onClick={onToggle}
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </Button>
    </motion.div>
  );
};