'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { Menu, X, LayoutDashboard, Calendar, Clock, CheckCircle2, Settings, ChevronLeft, ChevronRight, Bot, MessageSquare } from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import { SidebarChatPanel } from './SidebarChatPanel';

interface SidebarProps {
  isCollapsed?: boolean;
  onCollapseToggle?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed = false, onCollapseToggle }) => {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [showAiAssistant, setShowAiAssistant] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', href: '/', icon: LayoutDashboard },
    { id: 'my-tasks', label: 'My Tasks', href: '/tasks', icon: CheckCircle2 },
    { id: 'today', label: 'Today', href: '/today', icon: Calendar },
    { id: 'upcoming', label: 'Upcoming', href: '/upcoming', icon: Clock },
    { id: 'completed', label: 'Completed', href: '/completed', icon: CheckCircle2 },
    { id: 'settings', label: 'Settings', href: '/settings', icon: Settings },
  ];

  const toggleSidebar = () => {
    if (onCollapseToggle) {
      onCollapseToggle();
    }
  };

  // Mobile menu toggle
  const toggleMobileMenu = () => {
    setIsOpen(!isOpen);
  };

  // Toggle AI assistant panel
  const toggleAiAssistant = () => {
    setShowAiAssistant(!showAiAssistant);
  };

  // Render sidebar items
  const renderNavItems = () => (
    <nav className="mt-md">
      <ul className="space-y-xs">
        {navItems.map((item) => {
          const IconComponent = item.icon;
          const isActive = pathname === item.href;

          return (
            <li key={item.id}>
              <Link href={item.href} className="w-full">
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start gap-3 px-3 py-2 rounded-md",
                    isActive
                      ? "bg-primary text-primary-foreground shadow-none"
                      : "hover:bg-muted text-foreground",
                    !isCollapsed && "text-sm font-normal"
                  )}
                >
                  <IconComponent size={18} />
                  {!isCollapsed && <span>{item.label}</span>}
                </Button>
              </Link>
            </li>
          );
        })}

        {/* AI Assistant Button */}
        <li>
          <Button
            variant={showAiAssistant ? "secondary" : "ghost"}
            onClick={toggleAiAssistant}
            className={cn(
              "w-full justify-start gap-3 px-3 py-2 rounded-md",
              showAiAssistant
                ? "bg-primary text-primary-foreground shadow-none"
                : "hover:bg-muted text-foreground",
              !isCollapsed && "text-sm font-normal"
            )}
          >
            <Bot size={18} />
            {!isCollapsed && <span>AI Assistant</span>}
          </Button>
        </li>
      </ul>
    </nav>
  );

  return (
    <>
      {/* Mobile menu button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <Button
          variant="outline"
          size="icon"
          onClick={toggleMobileMenu}
          className="bg-background border-border text-foreground hover:bg-muted"
        >
          {isOpen ? <X size={18} /> : <Menu size={18} />}
        </Button>
      </div>

      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-40 md:hidden"
          onClick={toggleMobileMenu}
        />
      )}

      {/* Desktop Sidebar */}
      <motion.aside
        className={cn(
          "fixed inset-y-0 z-40 hidden md:block bg-background border-r border-border h-full",
          isCollapsed ? "w-16" : "w-64"
        )}
        initial={false}
        animate={{ width: isCollapsed ? 64 : 256 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <div className="flex flex-col h-full">
          {/* Logo/Collapse button */}
          <div className="flex items-center justify-between p-3 border-b border-border">
            {!isCollapsed && (
              <div className="text-lg font-semibold text-foreground pl-1">TodoSaaS</div>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleSidebar}
              className="ml-auto text-foreground hover:bg-muted"
            >
              {isCollapsed ? (
                <ChevronRight size={16} />
              ) : (
                <ChevronLeft size={16} />
              )}
            </Button>
          </div>

          {/* Navigation items or AI Assistant panel */}
          <div className="flex-1 overflow-y-auto p-2">
            {showAiAssistant && !isCollapsed ? (
              <SidebarChatPanel isExpanded={true} />
            ) : (
              <>
                {renderNavItems()}
              </>
            )}
          </div>
        </div>
      </motion.aside>

      {/* Mobile Sidebar */}
      <motion.aside
        className={cn(
          "fixed inset-y-0 z-50 bg-background border-r border-border h-full w-64 shadow-xl",
          isOpen ? "translate-x-0" : "-translate-x-full",
          "md:hidden transition-transform"
        )}
        initial={false}
        animate={{ x: isOpen ? 0 : -256 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <div className="flex flex-col h-full">
          {/* Logo/Collapse button */}
          <div className="flex items-center justify-between p-3 border-b border-border">
            <div className="text-lg font-semibold text-foreground pl-1">TodoSaaS</div>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleMobileMenu}
              className="text-foreground hover:bg-muted"
            >
              <X size={18} />
            </Button>
          </div>

          {/* Navigation items or AI Assistant panel */}
          <div className="flex-1 overflow-y-auto p-2">
            {showAiAssistant ? (
              <SidebarChatPanel isExpanded={true} />
            ) : (
              <>
                {renderNavItems()}
              </>
            )}
          </div>
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;