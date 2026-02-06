// Z-Index Management Utility
export const Z_INDEX = {
  // Background elements
  BACKGROUND: 0,
  BELOW_NORMAL: 10,

  // Normal elements
  NORMAL: 20,

  // UI elements
  SIDEBAR: 40,
  NAVBAR: 50,

  // Overlay elements
  MODAL_BACKDROP: 100,
  MODAL: 110,
  DROPDOWN: 120,
  POPOVER: 130,

  // Floating elements
  TOOLTIP: 140,
  NOTIFICATION: 150,
  FLOATING_BUTTON: 160,

  // Highest priority elements
  LOADING_OVERLAY: 200,
  TOPMOST: 9999,
} as const;

export type ZIndexKey = keyof typeof Z_INDEX;

/**
 * Get z-index value by key
 * @param key The z-index key from Z_INDEX
 * @returns The numeric z-index value
 */
export const getZIndex = (key: ZIndexKey): number => {
  return Z_INDEX[key];
};

/**
 * Get z-index class name for Tailwind CSS
 * @param key The z-index key from Z_INDEX
 * @returns The Tailwind CSS class name
 */
export const getZIndexClass = (key: ZIndexKey): string => {
  return `z-${Z_INDEX[key]}`;
};

/**
 * Utility function to manage sidebar z-index based on state
 * @param isCollapsed Whether the sidebar is collapsed
 * @param isVisible Whether the sidebar is visible
 * @returns The appropriate z-index value
 */
export const getSidebarZIndex = (isCollapsed: boolean, isVisible: boolean): number => {
  if (!isVisible) {
    return 0; // Hidden
  }
  return Z_INDEX.SIDEBAR;
};

/**
 * Utility function to manage AI assistant panel z-index
 * @param isChatOpen Whether the chat panel is open
 * @param isSidebarVisible Whether the sidebar is visible
 * @returns The appropriate z-index value
 */
export const getAiPanelZIndex = (isChatOpen: boolean, isSidebarVisible: boolean): number => {
  if (!isChatOpen) {
    return 0; // Hidden
  }
  // If sidebar is visible and chat is in sidebar, use sidebar z-index
  // Otherwise, use floating panel z-index
  return isSidebarVisible ? Z_INDEX.SIDEBAR + 1 : Z_INDEX.FLOATING_BUTTON;
};