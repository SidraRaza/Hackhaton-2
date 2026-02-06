import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from './ui/button';
import { cn } from '../lib/utils';

interface NavItemProps {
  id: string;
  label: string;
  href: string;
  icon?: React.ReactNode;
  isCollapsed?: boolean;
}

export const NavItem: React.FC<NavItemProps> = ({
  id,
  label,
  href,
  icon,
  isCollapsed
}) => {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <li key={id}>
      <Link href={href} className="w-full">
        <Button
          variant={isActive ? "secondary" : "ghost"}
          className={cn(
            "w-full justify-start gap-3 px-3 py-2.5 rounded-lg",
            isActive && "bg-primary text-primary-foreground",
            !isCollapsed && "text-base"
          )}
        >
          {icon}
          {!isCollapsed && <span>{label}</span>}
        </Button>
      </Link>
    </li>
  );
};