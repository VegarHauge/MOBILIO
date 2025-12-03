# Lab 7: Course Project

| Lab 7:      | Course Project              |
| ----------- | --------------------------- |
| Subject:    | DAT515 Cloud Computing      |
| Deadline:   | **November 14, 2025 23:59** |
| Grading:    | A-F                         |
| Submission: | Group                       |

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Project Deliverables](#project-deliverables)
  - [1. Design Document (design.md)](#1-design-document-designmd)
  - [2. Codebase](#2-codebase)
  - [3. Reproducibility Report (report.md)](#3-reproducibility-report-reportmd)
  - [4. Presentation Video](#4-presentation-video)
  - [5. Q\&A Session](#5-qa-session)
- [Project Selection Guidelines](#project-selection-guidelines)
  - [Specific Project Ideas](#specific-project-ideas)

The course project is meant to be a practical application of the concepts learned in the course.
You are free to choose any cloud computing technology or service to work with, tailored to your interests and skill level.

## Project Deliverables

Your project submission consists of five main deliverables:

### 1. Design Document (design.md)

Deadline: **September 19, 2025**

You are required to prepare a design document for your application.
The design doc should be brief, well-organized and easy to understand.
The design doc should be prepared in markdown format and named `design.md` and submitted in the project group's repository.
Remember that you can use [mermaid diagrams](https://github.com/mermaid-js/mermaid#readme) in markdown files.

The design doc **should include** the following sections:

- **Overview**: A brief description of the application and its purpose.
- **Architecture**: The high-level architecture of the application, including components, interactions, and data flow.
- **Technologies**: The cloud computing technologies or services used in the application.
- **Deployment**: The deployment strategy for the application, including any infrastructure requirements.

The design document should be updated throughout the development process and reflect the final implementation of your project.

Optional sections may include:

- Security: The security measures implemented in the application to protect data and resources.
- Scalability: The scalability considerations for the application, including load balancing and auto-scaling.
- Monitoring: The monitoring and logging strategy for the application to track performance and detect issues.
- Disaster Recovery: The disaster recovery plan for the application to ensure business continuity in case of failures.
- Cost Analysis: The cost analysis of running the application on the cloud, including pricing models and cost-saving strategies.
- References: Any external sources or references used in the design document.

### 2. Codebase

The codebase is the main deliverable for this project.
The project code should be well-organized, documented, and easily reproducible.
All source code and configuration files required to build and run the application must be included in your repository.

### 3. Reproducibility Report (report.md)

The `report.md` file serves as the primary documentation for your project and is critical for reproducibility.
It should include:

- **Project Overview**: Brief description of what the application does and its purpose.
- **Architecture Overview**: High-level description of the system architecture.
- **Prerequisites**: List of required software, tools, and dependencies.
- **Build Instructions**: Step-by-step commands to build the project from source.
- **Deployment Instructions**: Clear, reproducible steps to deploy the application.
- **Testing Instructions**: How to run tests (unit, integration, end-to-end).
- **Usage Examples**: How to use the application once deployed.
- **Presentation Video**: Link to your 10-minute presentation video.
- **Troubleshooting**: Common issues and their solutions.
- **Hour Sheet**: Time tracking for each group member showing hours spent on different activities.
- **Self-Assessment Table**: A detailed breakdown of tasks completed by each group member.

**Focus on Reproducibility**:
The deployment should be as simple as possible.
Anyone should be able to follow your instructions and successfully deploy your application.
Include all necessary configuration files, environment variables, and setup scripts.

**Assessment and Accountability**:
The report must include honest self-assessment and time tracking.
Each group member should accurately report their contributions and time spent on the project.
Each contribution should be linked to the specific commit on GitHub.
This information will be used for individual grading and to ensure fair contribution across team members.

**Report Template**:
Use the provided `report.md` template to structure your report.
This template includes all required sections and provides guidance on what information to include.
Simply overwrite the template content with your project-specific information.

**Use AI Tools**:
We strongly encourage teams to use AI tools to assist with code generation, documentation, and testing.
While we do encourage this, the team is ultimately responsible for ensuring the quality and accuracy of the final deliverables.
We recommend adding an `AGENTS.md` file to your repository to guide the AI to your project-specific requirements.

Please read what you can add to your `AGENTS.md` file over at [agents.md](https://agents.md).
Most AI tools should recognize the `AGENTS.md` file and use it to tailor their responses to your project's context.
(The `AGENTS.md` file replaces similar files like `copilot-instructions.md`, `CLAUDE.md`, and similar.)

### 4. Presentation Video

You are required to prepare a presentation video of your project.
The presentation video should be uploaded to YouTube and the link should be included in your `report.md` file.

#### Requirements

- Duration: 8-10 minutes (minimum 8 minutes, maximum 10 minutes)
- Upload to YouTube with a public or unlisted link
- Include the YouTube link in your `report.md` file
- Include clear audio narration throughout the video
- Include captions or subtitles if possible for accessibility

The presentation video **must include** the following components:

1. **Project Overview (1-2 minutes)**

   - Present the high-level architecture with diagrams
   - Explain the technologies and cloud services used
   - Describe the problem the project solves
   - Show system architecture diagrams and illustrations

2. **Project Demonstration (3-4 minutes)**

   - Show your application in action with a live demo or screen recording
   - Highlight the key features and functionality
   - Demonstrate the user interface and user experience

3. **Codebase Walk-through (2-3 minutes)**

   - Explain the project structure and organization
   - Walk through the key components and modules
   - Highlight important design decisions and technical choices
   - Show how different parts of the system interact

4. **Build and Deployment Showcase (2-3 minutes)**

   - Demonstrate how to build the project from source
   - Show the deployment process step-by-step
   - Explain any configuration or setup requirements
   - Demonstrate that the deployment instructions in `report.md` work

#### Video Preparation Tips

- **Planning & Structure**

  - Create a detailed script or outline before recording
  - Rehearse the presentation multiple times to stay within the time limit
  - Test your demo thoroughly to avoid technical difficulties during recording
  - Be prepared to redo sections if needed

- **Visual Quality**

  - Use screen recording software to capture demonstrations and slides
  - We recommend that you speed up _slow parts of your demonstration_ (e.g., compiling and building) during editing to fit the time constraints (but make sure it is still easy to follow)
  - Ensure all text and code shown in the video is readable
  - Use diagrams and visuals to explain concepts clearly
  - Keep visual consistency (font size, color scheme) throughout the video
  - Limit slides to key points; avoid dense text

- **Audio & Narration**

  - Speak at a steady pace, clearly articulating key points
  - Use simple language and avoid overloading with technical jargon
  - Consider using AI tools for audio enhancement or voice generation if needed
  - Ensure good audio quality - use a decent microphone

### 5. Q&A Session

- Criteria review against the checklist
- Each team member presents their work and receives feedback
- (More details about the format may be added later)

## Project Selection Guidelines

Your next step is to choose a project you want to pursue and describe its design in the design document, as [outlined above](#1-design-document-designmd).

Below are some specific ideas for projects that you can choose from.

> Several of these projects were generated by Copilot with only minor adjustments.
> Hence, do not take everything at face value, including the implementation and technology suggestions.
> You should evaluate the suggestions and adapt them to your preferred project idea.

You are free to propose your own project idea, as long as it aligns with the project requirements and satisfies the [project evaluation checklist](checklist.md).
When choosing your project, consider your experience, interests, and the level of complexity you’re comfortable with.
Each option offers a unique opportunity to explore cloud technologies and their deployment intricacies.

Each project team will get a responsible member of the teaching staff assigned to them.
This should be the main contact person to reach out to for guidance and support.
The responsible staff member names listed below are only tentative, and will be adjusted to balance the workload among the teaching staff.

### Specific Project Ideas

1. **QuickFeed Continuous Deployment**

   Modernize QuickFeed deployment with containerization and continuous deployment.

   In this project you will prepare container images for deploying the QuickFeed server to a test environment and then the production environment.
   The deployment environment should be configured to support Continuous Deployment.

   The current production version of Quickfeed runs on a virtual machine on one of UiS's Unix machines.
   However, development and testing in this environment result in a certain amount of fragility.
   Hence, we would like to move to a world where setting up and running a test environment is as simple as building and running a container or even simpler.

   **Core Goals (Required):**
   - Containerize the QuickFeed server with optimized Docker images
   - Create Docker Compose setup for local development/testing
   - Support multiple deployment environments for testing and production
   - Deploy to UiS Kubernetes environment
   - Add health checks and basic monitoring

   **Optional Enhancements (If Time Allows):**
   - Deploy to a cloud platform: Unikraft, fly.io, GCP, AWS, Azure
   - Implement rollback capabilities for failed deployments
   - Zero-downtime deployments with Kubernetes
   - Advanced monitoring with Prometheus and Grafana
   - Helm charts for Kubernetes deployment

   **Technology Suggestions:** Docker, Docker Compose, GitHub Actions, Kubernetes or cloud platform, basic monitoring

   **Responsible:** Hein

2. **QuickFeed: Running Student Tests with Kubernetes**

   In this project you will prepare a Kubernetes cluster to run student tests.
   This will involve interacting with Kubernetes API to deploy a container to run and test student submitted code.

   In this project we aim to scale QuickFeed to support more courses and users.
   One of the key challenges with QuickFeed is that we currently run tests of student code on every push to GitHub.
   This can cause a significant delay when many students are actively working on their assignments, or we manually trigger a rebuild.
   This is because each student submission is tested in a separate docker container running on the same virtual machine as the QuickFeed server.

   To scale QuickFeed, this project will implement deployment of the containers to a Kubernetes cluster with appropriate scheduling and task management.
   For this project, the Kubernetes cluster can be run locally on our OpenStack cluster machines.

   You may also consider doing this project using a serverless framework from one of the cloud providers.

   **Core Goals (Required):**
   - Set up local UiS Kubernetes cluster for development
   - Create Kubernetes Jobs for executing student tests flexible to support various courses
   - Implement basic queue system for test scheduling
   - Deploy test runner that produces test reports to QuickFeed
   - Basic resource limits and isolation for test containers

   **Optional Enhancements (If Time Allows):**
   - Test result aggregation and reporting dashboard
   - Deploy to cloud Kubernetes cluster
   - Implement horizontal pod autoscaling based on queue length
   - Add persistent volumes for test artifacts and logs
   - Implement advanced security policies for student code execution
   - Queue management with RabbitMQ or similar

   **Technology Suggestions:** Docker, Kubernetes, Go, basic queue system, GitHub webhooks

   **Responsible:** Hein

3. **Continuous Integration Test Framework for HotStuff**

   Build a testing infrastructure for the HotStuff Byzantine fault-tolerant consensus protocol.

   The Relab research group has implemented HotStuff variants that need better testing infrastructure.
   This project will create a modern CI system for testing consensus protocols.

   **Core Goals (Required):**
   - Set up GitHub Actions CI pipeline to deploy across bare-metal nodes
   - Distributed testing across multiple bare-metal nodes
   - Create basic test suite for consensus protocol validation
   - Integration with existing iago (ssh) tool
   - Containerize existing HotStuff implementation

   **Optional Enhancements (If Time Allows):**
   - Basic performance benchmarking and regression detection
   - Advanced Byzantine failure simulation capabilities
   - Implement simple network partition simulation
   - Advanced log analysis for consensus violations
   - Performance visualization dashboards with Grafana
   - Fuzz testing for protocol edge cases

   **Technology Suggestions:** Go, Docker, GitHub Actions, basic network emulation tools, Prometheus

   **Responsible:** Hein

4. **Stock Exchange Platform**

   Build a simplified stock trading platform with real-time order matching.

   **Core Goals (Required):**
   - Implement basic order book with buy/sell order matching
   - Create gRPC or REST API for placing orders and viewing portfolios
   - Build simple web interface for trading
   - Implement user authentication and basic portfolio management
   - Deploy to cloud platform with database persistence

   **Optional Enhancements (If Time Allows):**
   - Real-time WebSocket feeds for price updates
   - Support for multiple financial instruments
   - Advanced order types (limit, stop-loss, etc.)
   - Market data visualization and charts
   - Load balancing for high-frequency trading simulation
   - Redis caching for hot market data

   **Technology Suggestions:** Go, gRPC/REST APIs, PostgreSQL, React/Vue.js, WebSockets, cloud deployment

   **Responsible:** Hein or Jayachander

5. **Personal Finance Tracker**

   Build a comprehensive personal finance management application.

   **Core Goals (Required):**
   - User registration and authentication system
   - Manual transaction entry with categorization
   - Basic budget tracking and expense reporting
   - Simple dashboard with spending analytics
   - Cloud deployment with persistent data storage

   **Optional Enhancements (If Time Allows):**
   - Integration with banking APIs for automatic transaction import
   - Bill reminders and recurring payment tracking
   - Investment portfolio tracking with real-time prices
   - Multi-currency support with exchange rates
   - Advanced reporting and data visualization
   - Mobile-responsive design or PWA

   **Technology Suggestions:** React/Vue.js, Go, PostgreSQL, authentication system, cloud deployment

   **Responsible:** Hein or Jayachander

6. **Time Tracking and Payroll System**

   Build a lightweight payroll-style salary calendar where users log hours in a monthly calendar, confirm their pay period, and generate a PDF payslip.
   Students will get hands-on practice with authentication, data modeling, file storage, and basic document generation.

   **Core Goals (Required):**
   - User registration and authentication system
   - Time tracking interface with daily hour logging
   - Basic payroll calculation (hours × hourly rate)
   - PDF payslip generation for pay periods
   - Simple dashboard with time summaries and payslip history
   - Cloud deployment with persistent data storage

   **Optional Enhancements (If Time Allows):**
   - Calendar view for time entry and visualization
   - Multiple pay rates and overtime calculations
   - Manager approval workflow for timesheets
   - Email notifications for payslip generation
   - Data export functionality (CSV/Excel)
   - Mobile-responsive design or PWA
   - Advanced reporting and analytics
   - Integration with external calendar systems

   **Technology Suggestions:** React/Vue.js, Go, PostgreSQL, PDF generation library, cloud deployment

   **Responsible:** Haakon Webb

7. **Team Collaboration Tool for Student Projects**

   Build a real-time messaging application supporting group conversations for student projects.

   **Core Goals (Required):**
   - Channels, easy file sharing, and project groups.
   - Real-time messaging using WebSockets
   - Group chat rooms and direct messages
   - Message history persistence
   - Cloud deployment with scalable architecture
   - User authentication and profile management

   **Optional Enhancements (If Time Allows):**
   - File and image sharing capabilities
   - Message encryption for security
   - Typing indicators and read receipts
   - Push notifications for offline users
   - Message queues (RabbitMQ) for reliability
   - User presence tracking

   **Technology Suggestions:** Go, WebSockets, PostgreSQL/MongoDB, Redis, React/Vue.js

   **Responsible:** Foroozan.E

8. **Social Media Platform for University Recruitment**

   Build a SnapChat-like platform connecting prospective students with university resources.

   **Core Goals (Required):**
   - User profiles for students and university representatives
   - Content sharing (posts, images) with basic interactions (likes, comments)
   - Simple event management for university activities
   - Basic messaging system between users
   - Cloud deployment with content storage

   **Optional Enhancements (If Time Allows):**
   - Advanced recommendation algorithms for personalized content
   - Content moderation tools and reporting system
   - Multi-language support and localization
   - Integration with university databases
   - Analytics dashboard for engagement tracking
   - SEO optimization and advanced search

   **Technology Suggestions:** React/Vue.js, Go, PostgreSQL, cloud storage, content delivery

   **Responsible:** Ainaz

9. **File Storage Service**

   Build a cloud file storage service similar to Google Drive.

   **Core Goals (Required):**
   - File upload, download, and basic organization (folders)
   - User authentication and file ownership
   - File sharing with public/private links
   - Simple web interface for file management
   - Cloud deployment with object storage (S3/MinIO)

   **Optional Enhancements (If Time Allows):**
   - File versioning and conflict resolution
   - File synchronization across devices
   - File preview and thumbnail generation
   - Collaborative editing features
   - Advanced access control and permissions
   - File deduplication to save storage space

   **Technology Suggestions:** Go, React/Vue.js, MinIO/S3, PostgreSQL, cloud deployment

   **Responsible:** Ainaz

10. **E-commerce Platform**

    Develop a basic e-commerce platform with modern web technologies.

    **Core Goals (Required):**
    - Product catalog with search and basic filtering
    - Shopping cart and simple checkout process
    - User accounts with order history
    - Basic admin dashboard for product management
    - Payment integration (Stripe sandbox)

    **Optional Enhancements (If Time Allows):**
    - Product recommendation engine
    - Advanced inventory management with alerts
    - Multiple payment methods and currencies
    - Product reviews and ratings system
    - Email notifications for orders
    - CDN integration for product images

    **Technology Suggestions:** React/Vue.js, Go, PostgreSQL, Stripe API, cloud deployment

    **Responsible:** Haakon Webb

11. **Local Student Marketplace**

    Build a platform for students to buy, sell, and trade items locally.

    **Core Goals (Required):**
    - User accounts and profiles
    - Item listings with images and descriptions
    - Search and filtering options
    - In-app messaging between buyers and sellers
    - Location-based services (e.g., map integration)

    **Optional Enhancements (If Time Allows):**
    - Rating and review system for users
    - Payment integration (e.g., Stripe, PayPal)
    - Advanced search algorithms (e.g., machine learning)
    - Mobile app version for iOS/Android
    - Community features (e.g., forums, groups)

    **Technology Suggestions:** React/Vue.js, Go, PostgreSQL, cloud deployment

    **Responsible:** Foroozan.E

12. **Video Streaming Application**

    Build a basic video streaming platform for user-generated content.

    **Core Goals (Required):**
    - Video upload with basic processing (format conversion)
    - Video streaming with standard quality
    - User accounts and video management
    - Simple video player interface
    - Cloud deployment with video storage

    **Optional Enhancements (If Time Allows):**
    - Adaptive bitrate streaming (HLS/DASH)
    - Live streaming capabilities with RTMP
    - Video thumbnail generation and previews
    - Social features (comments, likes, subscriptions)
    - Content delivery network for global distribution
    - Video analytics and view tracking

    **Technology Suggestions:** Go, FFmpeg, React/Vue.js, cloud storage, streaming protocols

    **Responsible:** Jayachander

13. **Gaming Platform**

    Build a basic multiplayer gaming platform with simple games.

    **Core Goals (Required):**
    - User profiles and authentication
    - Simple turn-based game implementation (e.g., tic-tac-toe, checkers)
    - Real-time game sessions using WebSockets
    - Basic matchmaking system
    - Leaderboards and game history

    **Optional Enhancements (If Time Allows):**
    - Multiple game types and more complex games
    - Real-time multiplayer with game state synchronization
    - Tournament brackets and competitive seasons
    - Spectator mode and game replays
    - In-game chat and social features
    - Player statistics and performance analytics

    **Technology Suggestions:** Go, gRPC, WebSockets, Redis, PostgreSQL, Unity/Godot, Kubernetes

    **Responsible:** Jayachander
