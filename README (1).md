# Personalized Networking Assistant

## Task 1: Description of the ER Diagram

### Overview
The Personalized Networking Assistant stores user profiles, event contexts, networking sessions, AI-generated conversation starters, Wikipedia fact checks, and system logs.

## Entities Involved

- User Profile
- Event Context
- Networking Session
- Generated Starter
- Wikipedia Fact Check
- Log Entry

## Primary Keys

- UserID
- EventID
- SessionID
- StarterID
- FactCheckID
- LogID

## Relationships

- One User Profile can have many Networking Sessions.
- One Event Context can have many Networking Sessions.
- One Networking Session can generate many Conversation Starters.
- One Networking Session can have many Wikipedia Fact Checks.
- One Networking Session can have many Log Entries.

## Foreign Keys

- Networking Session references User Profile using UserID.
- Networking Session references Event Context using EventID.
- Generated Starter references Networking Session using SessionID.
- Wikipedia Fact Check references Networking Session using SessionID.
- Log Entry references Networking Session using SessionID.

## Purpose

This ER model is normalized to reduce redundancy and supports AI-generated conversation starters, fact verification, session tracking, and detailed system logging.
