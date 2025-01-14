# Kanban-Style Project Management System

## Project Overview
This project is a **Kanban-style project management system** developed as the final exam for CSE477 - Web Application Development. The system is inspired by Trello and designed to help teams manage projects through visual task organization and real-time collaboration.

I received a 95% on this project.

## Key Features

### Authentication & Access Control
- **User Authentication:** Secure signup and login system with encrypted password storage
- **Board Access Control:** Only invited members can access specific project boards
- **Session Management:** Secure user sessions with proper logout functionality

### Board Management
- **Create Boards:** Users can create new project boards and invite team members via email
- **Multiple Lists:** Each board contains three default lists: "To Do", "Doing", and "Completed"
- **Card Management:** 
  - Create, edit, and delete cards within lists
  - Real-time card content updates
  - Simultaneous editing prevention (card locking system)
  - Drag-and-drop functionality between lists

### Real-Time Collaboration
- **Live Updates:** All changes (new cards, edits, movements) are instantly visible to all active board members
- **Chat System:** Built-in chat functionality for real-time team communication
- **Active Member Tracking:** See which team members are currently viewing the board

## Technologies Used
- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python (Flask)
- **Database:** MySQL
- **Real-time Communication:** Socket.IO
- **Containerization:** Docker
- **Deployment:** Google Cloud Run

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [your-repository-url]
   cd [repository-name]
   ```

2. **Docker Setup**
   ```bash
   docker-compose up --build
   ```

3. **Access the Application**
   ```
   http://localhost:8080
   ```

## Usage Guide

### Creating a New Board
1. Create and Log in to your account
2. Click "Create New Board" on the home page
3. Enter project name and member emails
4. Click "Create Board"

### Managing Cards
1. Click "+" on any list to add a new card
2. Use drag-and-drop to move cards between lists
3. Click edit (✎) to modify card content
4. Click delete (×) to remove a card

### Using the Chat Feature
- Chat window is available at the bottom of each board
- Type messages and press Enter or click Send
- All active board members can participate in the chat

## Security Features
- Password encryption
- Session management
- Protected board access
- SQL injection prevention
- XSS protection

## Contributing
This project was developed as part of CSE477 coursework. While it's not open for contributions, you're welcome to fork the repository for personal use.

## Credits
- Course: CSE477 - Web Application Development
- Instructor: Dr. Mohammad Ghassemi
- Developer: Elias Asmar

## Contact
- **Name:** Elias Asmar
- **Email:** asmareli@msu.edu
- **GitHub:** [EliasSAsmar](https://github.com/EliasSAsmar)
