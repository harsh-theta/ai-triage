# Requirements Document

## Introduction

The AI Triage System is a proof-of-concept application that demonstrates intelligent, protocol-guided patient triage with emergency detection capabilities and structured data capture for Electronic Medical Records (EMR). The system uses conversational AI to guide patients through appropriate triage protocols, automatically detect emergency situations, and generate structured medical data suitable for healthcare providers.

## Requirements

### Requirement 1

**User Story:** As a patient, I want to describe my symptoms to an AI system, so that I can receive appropriate triage guidance and have my information structured for healthcare providers.

#### Acceptance Criteria

1. WHEN a patient starts a conversation THEN the system SHALL provide a welcoming greeting and ask for their chief complaint
2. WHEN a patient describes their symptoms THEN the system SHALL analyze and classify the complaint using AI
3. WHEN the system receives patient input THEN it SHALL maintain conversation state throughout the session
4. WHEN the conversation progresses THEN the system SHALL capture structured patient data for EMR integration

### Requirement 2

**User Story:** As a healthcare system, I want the AI to follow specific medical protocols based on patient complaints, so that consistent and appropriate questions are asked for different conditions.

#### Acceptance Criteria

1. WHEN the system classifies a headache complaint THEN it SHALL follow the headache-specific protocol with targeted questions
2. WHEN the system identifies a routine complaint THEN it SHALL follow general triage questioning patterns
3. WHEN following a protocol THEN the system SHALL ask relevant follow-up questions based on medical best practices
4. WHEN a protocol is active THEN the system SHALL indicate which protocol is being followed

### Requirement 3

**User Story:** As a healthcare provider, I want the system to immediately detect emergency situations, so that critical patients can be escalated to human care without delay.

#### Acceptance Criteria

1. WHEN a patient describes emergency symptoms THEN the system SHALL immediately flag the situation as an emergency
2. WHEN an emergency is detected THEN the system SHALL display a critical alert to connect the patient with a human doctor
3. WHEN in emergency mode THEN the system SHALL disable further AI interaction to prevent delays
4. WHEN an emergency is flagged THEN the system SHALL clearly communicate the urgency to the patient

### Requirement 4

**User Story:** As a healthcare provider, I want to see structured EMR data generated from the conversation, so that I can quickly understand the patient's condition and history.

#### Acceptance Criteria

1. WHEN the conversation progresses THEN the system SHALL continuously update structured patient data
2. WHEN data is captured THEN it SHALL be formatted in a JSON structure suitable for EMR systems
3. WHEN the triage is complete THEN the system SHALL provide a comprehensive summary of findings
4. WHEN displaying EMR data THEN it SHALL be presented in a clear, readable format for healthcare providers

### Requirement 5

**User Story:** As a user of the demo system, I want a professional and intuitive chat interface, so that the interaction feels natural and trustworthy.

#### Acceptance Criteria

1. WHEN using the chat interface THEN messages SHALL be clearly distinguished between AI and user
2. WHEN the AI is processing THEN the system SHALL show typing indicators for natural interaction
3. WHEN messages are sent THEN the chat window SHALL automatically scroll to show the latest message
4. WHEN the interface loads THEN it SHALL display both the chat area and EMR data preview side-by-side

### Requirement 6

**User Story:** As a system administrator, I want the application to run reliably with the specified tech stack, so that it can be demonstrated effectively to stakeholders.

#### Acceptance Criteria

1. WHEN the backend starts THEN it SHALL use FastAPI with LangGraph for AI orchestration
2. WHEN the frontend loads THEN it SHALL use React with Vite, shadcn/ui, and Tailwind CSS
3. WHEN making AI requests THEN the system SHALL use Google Gemini API for natural language processing
4. WHEN managing state THEN conversation data SHALL be maintained in memory per session without requiring a database