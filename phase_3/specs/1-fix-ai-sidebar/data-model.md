# Data Model for Fix AI Assistant Sidebar Issue

Based on the key entities identified in the feature specification, here are the relevant data models:

## ChatMessage Entity
Represents a message in the chatbot conversation with the following attributes:
- **id**: Unique identifier (UUID/string)
- **sender**: Enum (user/assistant), required
- **content**: String, required (cannot be empty)
- **timestamp**: Timestamp, auto-generated
- **status**: Enum (sent/delivered/read), default: sent
- **type**: Enum (text/command/response), default: text

**Validation rules**:
- Content must not be empty
- Sender must be one of allowed values (user, assistant)
- Timestamp is managed automatically

## SidebarState Entity
Represents the state of the sidebar with the following attributes:
- **id**: Unique identifier (UUID/string)
- **isVisible**: Boolean, default: true
- **isCollapsed**: Boolean, default: false
- **width**: Number, default: 320 (pixels)
- **position**: Enum (left/right), default: left
- **lastUpdated**: Timestamp, auto-generated

**Validation rules**:
- isVisible must be boolean
- isCollapsed must be boolean
- width must be positive number
- lastUpdated is managed automatically

## AssistantConfig Entity
Represents configuration for the AI assistant with the following attributes:
- **id**: Unique identifier (UUID/string)
- **serviceEndpoint**: String, required
- **isAvailable**: Boolean, default: true
- **displayPreferences**: Object, default: {}
- **lastConnectionCheck**: Timestamp, auto-generated
- **status**: Enum (online/offline/error), default: online

**Validation rules**:
- serviceEndpoint must be valid URL format
- isAvailable must be boolean
- lastConnectionCheck is managed automatically
- status must be one of allowed values