import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        width, height = letter
        
        # Primary Color Palette
        navy = colors.HexColor("#0A2540")
        gold = colors.HexColor("#D4AF37")
        light_gray = colors.HexColor("#E2E8F0")
        text_gray = colors.HexColor("#64748B")

        # Top Header Line & Title for Page 2+
        if self._pageNumber > 1:
            self.setFillColor(navy)
            self.setFont("Helvetica-Bold", 8)
            self.drawString(54, height - 32, "ONGC AI Knowledge Assistant — Technical Project Report")
            
            self.setStrokeColor(light_gray)
            self.setLineWidth(0.75)
            self.line(54, height - 38, width - 54, height - 38)
            
            # Gold Accent Bar below header line
            self.setStrokeColor(gold)
            self.setLineWidth(2)
            self.line(54, height - 38, 180, height - 38)

        # Footer on all pages
        self.setStrokeColor(light_gray)
        self.setLineWidth(0.75)
        self.line(54, 42, width - 54, 42)

        self.setFont("Helvetica", 8)
        self.setFillColor(text_gray)
        self.drawString(54, 28, "Confidential — ONGC Policy Monitoring & Control (PMC) Section")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(width - 54, 28, page_str)
        
        self.restoreState()


def create_pdf_report(filename):
    pdf_path = os.path.abspath(filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=46,
        bottomMargin=50
    )

    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Palette
    navy = colors.HexColor("#0A2540")
    dark_red = colors.HexColor("#A81C1C")
    gold = colors.HexColor("#D4AF37")
    slate_dark = colors.HexColor("#1E293B")
    slate_body = colors.HexColor("#334155")
    bg_light = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#CBD5E1")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=navy,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=dark_red,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=navy,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=dark_red,
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=slate_body,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=slate_body,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=slate_dark
    )

    code_style = ParagraphStyle(
        'Code_Block',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=slate_dark
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("ONGC AI Knowledge Assistant", title_style))
    story.append(Paragraph("Enterprise Offline RAG Chatbot & Technical Architecture Report", subtitle_style))
    
    meta_data = [
        [
            Paragraph("<b>Organization:</b> Oil and Natural Gas Corporation (ONGC)", table_cell_style),
            Paragraph("<b>Project Status:</b> Production Ready (v1.0.0)", table_cell_style)
        ],
        [
            Paragraph("<b>Department:</b> Policy Monitoring & Control (PMC)", table_cell_style),
            Paragraph("<b>Security Level:</b> 100% Offline / Local Network", table_cell_style)
        ],
        [
            Paragraph("<b>Division:</b> Corporate Materials Management, New Delhi", table_cell_style),
            Paragraph("<b>Date:</b> July 2026", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 244])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Executive Summary Section
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=4))
    
    exec_summary_text = (
        "The <b>ONGC AI Knowledge Assistant</b> is an enterprise-grade, fully offline Artificial Intelligence "
        "chatbot engineered to query ONGC internal manuals, policy documents, and procurement guidelines securely and instantly. "
        "Built using a local <b>Retrieval-Augmented Generation (RAG)</b> pipeline, the system operates entirely within "
        "ONGC's isolated network environment without relying on external cloud APIs, eliminating third-party data privacy risks.<br/>"
        "The system combines local LLMs via Ollama, ChromaDB vector storage, a FastAPI web backend, and an intuitive "
        "web dashboard featuring real-time token streaming, multi-session memory, PDF drag-and-drop ingestion, voice controls, and analytics."
    )
    story.append(Paragraph(exec_summary_text, body_style))
    story.append(Spacer(1, 4))

    # Highlight Box
    callout_data = [[
        Paragraph("<b>Zero-Cloud Security Architecture:</b> All document parsing, embeddings generation, vector similarity searches, and LLM inferences execute locally on ONGC workstation hardware, complying fully with enterprise security policies.", callout_style)
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('LINELEFT', (0,0), (-1,-1), 3.5, navy),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 6))

    # Key Features
    story.append(Paragraph("2. Core Features & Capabilities", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=4))
    
    features = [
        ("<b>Offline RAG Pipeline:</b>", "Answers user queries strictly grounded in indexed PDF manuals, eliminating AI hallucination."),
        ("<b>Local LLM Flexibility:</b>", "Dynamic switching across local models including <code>Llama 3.2 (1B/3B)</code>, <code>Qwen 2.5</code>, and <code>Gemma 3</code> via Ollama."),
        ("<b>Persistent Vector Storage:</b>", "ChromaDB database powered by <code>sentence-transformers/all-MiniLM-L6-v2</code> dense embeddings."),
        ("<b>Real-Time Token Streaming:</b>", "FastAPI Server-Sent Events (SSE) stream responses token-by-token for ultra-responsive interaction."),
        ("<b>Multi-Session Web UI:</b>", "Browser <code>localStorage</code> session management with light/dark themes and responsive sidebar."),
        ("<b>Document Ingestion Engine:</b>", "Drag-and-drop PDF parser with character chunking (500 size, 50 overlap) and auto-indexing."),
        ("<b>User Feedback & Analytics:</b>", "SQLite rating database tracking thumbs up/down, user comments, and satisfaction metrics."),
        ("<b>Voice Interface & Dockerization:</b>", "Native Web Speech STT/TTS voice integration and complete Docker Compose deployment container.")
    ]

    for title, desc in features:
        story.append(Paragraph(f"• {title} {desc}", bullet_style))

    story.append(Spacer(1, 6))

    # Architecture Table
    story.append(Paragraph("3. System Architecture & Technology Stack", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=4))

    stack_data = [
        [Paragraph("Architecture Layer", table_header_style), Paragraph("Technology / Framework", table_header_style), Paragraph("Implementation Details & Responsibility", table_header_style)],
        [Paragraph("Frontend UI", table_cell_style), Paragraph("HTML5, CSS3, Vanilla JS", table_cell_style), Paragraph("Single-page app, Glassmorphism design system, Web Speech API, theme toggle", table_cell_style)],
        [Paragraph("Backend API", table_cell_style), Paragraph("FastAPI + Uvicorn", table_cell_style), Paragraph("Async REST endpoints, streaming SSE response handler, static route mounting", table_cell_style)],
        [Paragraph("RAG Orchestration", table_cell_style), Paragraph("LangChain Framework", table_cell_style), Paragraph("Prompt engineering, document context formatting, session history assembly", table_cell_style)],
        [Paragraph("Local LLM Engine", table_cell_style), Paragraph("Ollama API Host", table_cell_style), Paragraph("Offline inference runtime hosting Llama 3.2, Qwen 2.5, and Gemma 3 models", table_cell_style)],
        [Paragraph("Embeddings Model", table_cell_style), Paragraph("all-MiniLM-L6-v2", table_cell_style), Paragraph("384-dimensional dense sentence transformer running in offline mode", table_cell_style)],
        [Paragraph("Vector Database", table_cell_style), Paragraph("ChromaDB", table_cell_style), Paragraph("Persistent similarity search vector database with HNSW indexing", table_cell_style)],
        [Paragraph("Feedback DB", table_cell_style), Paragraph("SQLite (feedback.db)", table_cell_style), Paragraph("Stores conversation metrics, user ratings, and feedback comments", table_cell_style)],
        [Paragraph("Deployment", table_cell_style), Paragraph("Docker & Compose", table_cell_style), Paragraph("Multi-stage container with persistent volume mounts for docs & vector DB", table_cell_style)]
    ]

    stack_table = Table(stack_data, colWidths=[105, 125, 274])
    stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(stack_table)
    story.append(Spacer(1, 6))

    # Modules Section
    story.append(Paragraph("4. Key Software Modules", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=4))

    modules = [
        ("main.py", "FastAPI server exposing REST endpoints (<code>/api/chat</code>, <code>/api/ingest</code>, <code>/api/documents</code>, <code>/api/analytics</code>)."),
        ("app/rag.py", "Core RAG logic supporting standard responses and SSE streaming token generation (<code>run_rag_pipeline_stream</code>)."),
        ("utils/vectorstore.py", "ChromaDB CRUD store manager, similarity retriever factory, and document deduplication check."),
        ("utils/loader.py", "PDF text extractor utilizing <code>PyPDFLoader</code> and <code>RecursiveCharacterTextSplitter</code> (500 size, 50 overlap)."),
        ("ingest.py", "CLI bulk PDF ingestion utility for populating ChromaDB from the <code>docs/</code> repository in offline mode."),
        ("app/memory.py", "Session-based chat memory manager maintaining multi-turn context per user session ID.")
    ]

    for mod_name, mod_desc in modules:
        story.append(Paragraph(f"• <b><code>{mod_name}</code></b> — {mod_desc}", bullet_style))

    story.append(Spacer(1, 6))

    # Repository Structure
    story.append(Paragraph("5. Repository Directory & File Structure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=4))

    repo_structure_text = (
        "ONGC_CHATBOT/\n"
        "|-- app/\n"
        "|   |-- config.py           # Paths, model defaults, hyperparameter settings\n"
        "|   |-- chatbot.py          # Top-level chatbot wrapper\n"
        "|   |-- memory.py           # Session conversation history memory manager\n"
        "|   +-- rag.py              # Core RAG retrieval & SSE streaming pipeline\n"
        "|-- utils/\n"
        "|   |-- embeddings.py       # Offline HuggingFace embeddings singleton\n"
        "|   |-- loader.py           # PDF document loader & text chunker\n"
        "|   +-- vectorstore.py      # ChromaDB CRUD vector store operations\n"
        "|-- prompts/\n"
        "|   +-- system_prompt.py    # ONGC enterprise system prompt template\n"
        "|-- templates/\n"
        "|   +-- index.html          # Web dashboard HTML structure\n"
        "|-- static/\n"
        "|   |-- style.css           # Custom CSS styling (dark/light themes)\n"
        "|   +-- app.js              # Frontend Javascript (chat, voice, ingestion)\n"
        "|-- docs/                   # PDF knowledge base directory\n"
        "|-- chroma_db/              # Persistent ChromaDB vector database\n"
        "|-- main.py                 # FastAPI application main server\n"
        "|-- ingest.py               # PDF document ingestion CLI tool\n"
        "|-- Dockerfile              # Container deployment script\n"
        "+-- docker-compose.yml      # Multi-container orchestration config"
    )
    
    struct_table = Table([[Paragraph(repo_structure_text.replace('\n', '<br/>'), code_style)]], colWidths=[504])
    struct_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(struct_table)
    story.append(Spacer(1, 6))

    # Deployment & Operations Guide wrapped in KeepTogether
    ops_flowables = [
        Paragraph("6. Operations & Deployment Guide", h1_style),
        HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=4),
        Paragraph("<b>Option A: Standard Python Virtual Environment</b>", h2_style),
        Paragraph("1. Start Ollama local LLM service: <code>ollama serve</code>", bullet_style),
        Paragraph("2. Ingest PDF manuals into ChromaDB: <code>python ingest.py</code>", bullet_style),
        Paragraph("3. Launch web server: <code>python -m uvicorn main:app --host 127.0.0.1 --port 8000</code>", bullet_style),
        Paragraph("4. Open dashboard in web browser: <code>http://127.0.0.1:8000</code>", bullet_style),
        Spacer(1, 3),
        Paragraph("<b>Option B: Docker Container Deployment</b>", h2_style),
        Paragraph("Run <code>docker-compose up --build -d</code> to launch containerized services. Persistent volumes ensure <code>chroma_db/</code>, <code>docs/</code>, and <code>feedback.db</code> data are preserved across container updates.", body_style)
    ]
    story.append(KeepTogether(ops_flowables))

    story.append(Spacer(1, 6))

    # Roadmap & Sign-off wrapped in KeepTogether
    roadmap_flowables = [
        Paragraph("7. Future Roadmap & Strategic Enhancements", h1_style),
        HRFlowable(width="100%", thickness=1.2, color=gold, spaceAfter=4),
        Paragraph("• <b>Hybrid Search (Dense + Sparse):</b> Integrate BM25 keyword matching alongside vector search for accurate clause number retrieval.", bullet_style),
        Paragraph("• <b>OCR & Multi-Modal Processing:</b> Incorporate PaddleOCR to index scanned image-based historical ONGC policy documents.", bullet_style),
        Paragraph("• <b>Role-Based Access Control (RBAC):</b> Enforce document-level access permissions based on employee department authorization levels.", bullet_style),
        Paragraph("• <b>Multilingual Capabilities:</b> Support seamless English to Hindi query transformation using dedicated Hindi fine-tuned checkpoints.", bullet_style),
        Spacer(1, 10),
        Table([
            [
                Paragraph("<b>Prepared By:</b><br/>ONGC Summer Internship Project Team", table_cell_style),
                Paragraph("<b>Approved By:</b><br/>PMC Section, Corporate MM, New Delhi", table_cell_style)
            ]
        ], colWidths=[250, 254], style=[
            ('LINEABOVE', (0,0), (-1,-1), 1, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ])
    ]
    story.append(KeepTogether(roadmap_flowables))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at: {pdf_path}")

if __name__ == "__main__":
    output_pdf = "ONGC_AI_Assistant_Project_Report.pdf"
    create_pdf_report(output_pdf)
