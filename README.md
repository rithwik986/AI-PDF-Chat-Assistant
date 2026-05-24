# AI-Powered Research and Interview Preparation Assistant

The AI-Powered Research and Interview Preparation Assistant is an LLM-powered document intelligence platform designed to help users interact with PDF documents conversationally using natural language. The main objective of the project was to simplify the process of understanding lengthy PDFs such as research papers, technical reports, and study materials without manually reading the entire document.

Initially, the project was able to summarize uploaded PDFs, but the interaction ended after generating the summary. Users could not continue asking contextual questions from the uploaded document. To solve this limitation, the system was redesigned into an interactive conversational AI platform where users can continuously interact with uploaded PDFs just like ChatGPT.

The application allows users to upload PDFs, ask follow-up questions, generate academically focused quiz questions, and generate interview-oriented questions from the uploaded document. The academic quiz module helps users revise concepts and prepare for exams, while the interview module focuses more on technical and conceptual interview preparation.

The system was developed using Flask for the backend, HTML/CSS/JavaScript for the frontend, PyPDF2 for PDF text extraction, MySQL with SQLAlchemy for database management, and Gemini 2.5 Flash API for AI response generation. The workflow includes PDF upload, text extraction, preprocessing and cleaning, prompt engineering, contextual AI interaction, and response generation.

One of the biggest challenges faced during development was handling large PDF content within LLM token limitations while maintaining contextual relevance. Another challenge was transforming the project from a simple summarization system into a fully interactive conversational document assistant. These issues were addressed using text preprocessing, context truncation, optimized prompt engineering, and conversational memory handling.

The project demonstrates practical usage of LLM APIs beyond a simple chatbot wrapper by combining conversational AI, contextual document interaction, educational workflows, interview preparation features, and prompt-based document intelligence into a unified AI-powered platform.
