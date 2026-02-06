'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/src/components/ui/button';
import { useTheme } from '@/src/contexts/ThemeContext';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, onClose }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <motion.div
      initial={{ opacity: 0, x: '100%' }}
      animate={{ opacity: isOpen ? 1 : 0, x: isOpen ? 0 : '100%' }}
      exit={{ opacity: 0, x: '100%' }}
      transition={{ type: 'tween', duration: 0.2 }}
      className={`fixed inset-y-0 right-0 z-50 w-64 bg-background border-l border-border shadow-lg ${
        isOpen ? 'block' : 'hidden'
      }`}
    >
      <div className="p-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-foreground">Menu</h2>
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        <nav className="flex flex-col space-y-2">
          <Button variant="ghost" className="justify-start">
            Dashboard
          </Button>
          <Button variant="ghost" className="justify-start">
            My Tasks
          </Button>
          <Button variant="ghost" className="justify-start">
            Today
          </Button>
          <Button variant="ghost" className="justify-start">
            Upcoming
          </Button>
          <Button variant="ghost" className="justify-start">
            Completed
          </Button>
          <Button variant="ghost" className="justify-start">
            Settings
          </Button>
        </nav>

        <div className="mt-8">
          <Button variant="outline" onClick={toggleTheme} className="w-full">
            {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          </Button>
        </div>
      </div>
    </motion.div>
  );
};

export default MobileMenu;