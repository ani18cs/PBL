import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_presentation_pdf(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Custom harmonious color palette
    primary_color = colors.HexColor('#1e3a8a')   # Deep Navy
    secondary_color = colors.HexColor('#0284c7') # Sky Blue
    body_color = colors.HexColor('#334155')      # Charcoal Slate
    bg_light = colors.HexColor('#f8fafc')        # Very Light Grey/Blue
    accent_alert = colors.HexColor('#dc2626')    # Alert Red
    border_color = colors.HexColor('#e2e8f0')    # Light grey border

    # Custom styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=primary_color,
        spaceAfter=5,
        alignment=1 # Centered
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=25,
        alignment=1 # Centered
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=primary_color,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=secondary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=body_color,
        leading=14,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        textColor=colors.HexColor('#0f172a'),
        leading=11
    )

    eli5_header_style = ParagraphStyle(
        'ELI5Header',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        textColor=secondary_color,
        spaceAfter=3
    )

    eli5_body_style = ParagraphStyle(
        'ELI5Body',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        textColor=colors.HexColor('#0f766e'),
        leading=13
    )

    q_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    a_style = ParagraphStyle(
        'AnswerStyle',
        parent=body_style,
        leftIndent=12,
        spaceAfter=10
    )

    # -------------------------------------------------------------------------
    # Helper Components
    # -------------------------------------------------------------------------
    def add_eli5_box(title, text):
        box_data = [
            [Paragraph(f"🧒 <b>Explain Like I'm 10: {title}</b>", eli5_header_style)],
            [Paragraph(text, eli5_body_style)]
        ]
        t = Table(box_data, colWidths=[510])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdfa')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#99f6e4')),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(Spacer(1, 4))
        story.append(t)
        story.append(Spacer(1, 8))

    def add_code_block(code_lines):
        formatted_code = "<br/>".join(code_lines).replace(" ", "&nbsp;")
        t = Table([[Paragraph(formatted_code, code_style)]], colWidths=[510])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(Spacer(1, 4))
        story.append(t)
        story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # PDF CONTENT GENERATION
    # -------------------------------------------------------------------------
    
    # Title & Metadata
    story.append(Spacer(1, 20))
    story.append(Paragraph("DEFCON-D DDoS Platform", title_style))
    story.append(Paragraph("Professor Presentation Guide & Comprehensive Reference Manual", subtitle_style))
    story.append(Spacer(1, 15))

    # --- SECTION 1: INTRODUCTION & TECH STACK ---
    story.append(Paragraph("1. Project Overview & Tech Stack", h1_style))
    story.append(Paragraph(
        "<b>DEFCON-D</b> is an interactive, sandbox-style cybersecurity range built for teaching, demonstrating, "
        "and mitigating <b>Distributed Denial of Service (DDoS)</b> attacks in real time. Rather than using "
        "complex pre-built security packages, this system implements low-level network server routines, math algorithms, "
        "and responsive firewalls directly in clean Python modules.", body_style
    ))

    # ELI5: What is DDoS
    add_eli5_box(
        "What is a DDoS Attack?",
        "Imagine you run a popular ice cream shop. A bully wants to ruin your business, so they hire 100 people to fill "
        "your shop and stand in line forever without buying anything. When real, hungry customers try to get in, the "
        "shop is so packed that they can't even open the door! That is a DDoS attack. The bully is a hacker, the fake "
        "shoppers are computers, and your ice cream shop is a server."
    )

    story.append(Paragraph("<b>The Technical Stack</b>", h2_style))
    story.append(Paragraph("Our system uses the following technologies to model a complete production lifecycle:", body_style))
    
    tech_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Why We Used It</b>", body_style)],
        ["Core Language", "Python 3.12+", "Excellent standard libraries for multithreading, sockets, and math modules."],
        ["TCP Server", "Python socket module", "Enables low-level socket bind/listen/accept, measuring exact request latency."],
        ["Web / APIs", "Flask", "Creates lightweight REST routes for simulator actions and serving HTML template files."],
        ["Real-time Pipeline", "Flask-SocketIO / WebSockets", "Streams server alerts, traffic statistics, and system logs to UI every 1.0s."],
        ["Database Store", "SQLite 3", "Stores metrics, threat history, and firewall logs in local relational tables."],
        ["PDF Generation", "ReportLab", "Compiles live metrics and generates custom research reports directly on the server."]
    ]
    t_tech = Table(tech_data, colWidths=[110, 140, 260])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # Page Break for next section
    story.append(PageBreak())

    # --- SECTION 2: SYSTEM ARCHITECTURE & CODE MODULES ---
    story.append(Paragraph("2. How the Backend Systems Work", h1_style))
    story.append(Paragraph(
        "The project is structured into modular layers, separating traffic logic, logging, anomaly detection, and "
        "mitigation scripts. This ensures clean maintainability and matches modern system design principles.", body_style
    ))

    # ELI5: Tech stack things
    add_eli5_box(
        "What does each part do?",
        "• <b>The TCP Server:</b> The gatekeeper. It accepts customers and asks them what they want.<br/>"
        "• <b>The Simulator:</b> The actor. It creates the 'bully' computers that pretend to be normal customers.<br/>"
        "• <b>The Database:</b> The memory. It writes down everything that happens in a digital notebook.<br/>"
        "• <b>The Detection Engine:</b> The detective. It watches how fast customers arrive and reports if they are suspicious.<br/>"
        "• <b>The Mitigation Engine:</b> The bouncer. It blocks bad customers from entering and locks the door for spammy IPs."
    )

    story.append(Paragraph("<b>Backend Component Breakdown</b>", h2_style))
    story.append(Paragraph("• <b>Target Server (<code>server/target_server.py</code>)</b>: Creates a raw socket server bound to port <code>8080</code>. When a connection is accepted, it starts a client thread to process the request, returning HTTP responses. It also has a background daemon that aggregates performance logs.", bullet_style))
    story.append(Paragraph("• <b>Connection Manager (<code>server/connection_manager.py</code>)</b>: A thread-safe metrics accumulator. It locks statistics buffers during updates to prevent concurrency race conditions.", bullet_style))
    story.append(Paragraph("• <b>Traffic Generator (<code>simulator/traffic_generator.py</code>)</b>: Spawns virtual clients using a ThreadPoolExecutor. It uses randomized delay jitters to prevent synthetic syncing, and includes safety guardrails to block target URLs targeting public domains.", bullet_style))
    story.append(Paragraph("• <b>Database Schema (<code>database/database.py</code>)</b>: Automatically initializes SQLite tables. Saves metrics, security alerts, and mitigation logs with indexed relational keys.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Target Server Sockets Setup:</b>", h2_style))
    add_code_block([
        "self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)",
        "self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)",
        "self.server_socket.bind((self.host, self.port))",
        "self.server_socket.listen(128)",
        "# Spawns background listener thread",
        "self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)"
    ])

    story.append(PageBreak())

    # --- SECTION 3: DDOS DETECTION MATH ---
    story.append(Paragraph("3. Anomaly Detection and Mathematics", h1_style))
    story.append(Paragraph(
        "Rather than matching known signatures, DEFCON-D analyzes traffic dynamics every second. "
        "It evaluates three core indicators: overall Request Rates, Sudden Burst Spikes, and Shannon Entropy.", body_style
    ))

    add_eli5_box(
        "Shannon Entropy & IP Diversity",
        "Imagine you have a bag of 10 candies. <br/>"
        "<b>Case A (High Surprise / Diverse legimate traffic)</b>: You have 10 candies, each a different color. "
        "If you pull one out, you have no idea what color it will be! It is a big surprise. This is high entropy. "
        "High entropy is healthy—it means lots of different people are using your website.<br/>"
        "<b>Case B (Zero Surprise / Targeted attack)</b>: You have 10 candies, but ALL 10 are red. "
        "If you pull one out, it is guaranteed to be red! There is zero surprise. This is low entropy. "
        "Low entropy means a single IP is spamming the server, triggering a Red alert."
    )

    story.append(Paragraph("<b>Mathematical Formulations</b>", h2_style))
    story.append(Paragraph(
        "<b>1. Moving Average Burst Detection</b>: Compares current requests/sec (PPS) against a rolling "
        "10-second history window. If traffic exceeds this moving average by a factor of <b>2.5x</b>, an anomaly "
        "alert is triggered.", body_style
    ))
    
    story.append(Paragraph(
        "<b>2. Shannon Entropy of Source IP Distribution</b>: Measures randomness bits. Lower values indicate "
        "extremely concentrated source IP ranges (focused flood attacks):", body_style
    ))
    
    # Mathematical block display
    formula_data = [
        [Paragraph("<font size='12'><b>Shannon Entropy Formula:</b></font>", body_style)],
        [Paragraph("<font face='Courier' size='11'>H(X) = - ∑ P(x_i) * log2(P(x_i))</font>", title_style)],
        [Paragraph("Where P(x_i) is the probability (ratio) of requests from a specific source IP inside the current second.", body_style)]
    ]
    t_form = Table(formula_data, colWidths=[510])
    t_form.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_form)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # --- SECTION 4: MITIGATION MECHANISMS ---
    story.append(Paragraph("4. Defensive Mitigation Strategies", h1_style))
    story.append(Paragraph(
        "When an anomaly or signature is detected, DEFCON-D can deploy three firewall countermeasures "
        "automatically to defend the target system resources:", body_style
    ))

    add_eli5_box(
        "Mitigation Systems",
        "• <b>Connection Limit:</b> A family rule. A family can only order 8 ice creams at a time. If they try to buy 9, they are kicked out.<br/>"
        "• <b>Rate Limiter:</b> A pacing rule. You can only ask for ice cream once every 10 seconds. If you ask faster, we say 'Wait!'.<br/>"
        "• <b>Firewall Blacklist:</b> The bouncer's notebook. If you break the pacing or family rules, the bouncer writes your name down. "
        "For the next 30 seconds, if you walk up to the door, the bouncer locks it before you can say a word."
    )

    story.append(Paragraph("<b>Mitigation Algorithms</b>", h2_style))
    story.append(Paragraph("• <b>Sliding-Window Rate Limiting (<code>mitigation/rate_limiter.py</code>)</b>: Monitors request frequency per IP. Uses standard lock synchronization to manage timestamps within the last 1.0s window. Rejects requests exceeding 15 req/s with HTTP 429.", bullet_style))
    story.append(Paragraph("• <b>Concurrency Limiting (<code>mitigation/connection_limiter.py</code>)</b>: Restricts open TCP sockets per client IP to a maximum of 8 active sessions, protecting system socket descriptors from exhaustion.", bullet_style))
    story.append(Paragraph("• <b>Blacklist Manager (<code>mitigation/blacklist_manager.py</code>)</b>: A temporary IP blocker. Connections from blacklisted IPs are dropped instantly at the listener socket accept stage. Features auto-aging unblock threads to clean up rules automatically once timers expire.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Sliding-Window Implementation Snippet:</b>", h2_style))
    add_code_block([
        "now = time.time()",
        "with self.lock:",
        "    # Purge timestamps older than 1.0 second",
        "    self.request_windows[ip] = [t for t in self.request_windows[ip] if now - t < 1.0]",
        "    if len(self.request_windows[ip]) >= self.limit:",
        "        return True  # Rate limited!",
        "    self.request_windows[ip].append(now)",
        "    return False"
    ])

    story.append(PageBreak())

    # --- SECTION 5: PRESENTATION AND Q&A ---
    story.append(Paragraph("5. Presentation Flow & Question Prep", h1_style))
    story.append(Paragraph(
        "Here are key questions your professors are likely to ask during the project defense, "
        "along with the exact structured answers you should provide.", body_style
    ))

    # Q1
    story.append(Paragraph("Q: Why did you write a custom TCP socket server instead of using frameworks like Django or FastAPI?", q_style))
    story.append(Paragraph(
        "A: Frameworks abstract away the low-level transport layer. By writing a raw socket handler in Python "
        "(`socket.socket`), we can accept connections, measure processing latencies, and drop malicious packets "
        "immediately at the socket layer before they consume application-level memory pools.", a_style
    ))

    # Q2
    story.append(Paragraph("Q: How does Shannon Entropy benefit DDoS detection compared to standard threshold metrics?", q_style))
    story.append(Paragraph(
        "A: Standard threshold filters (like PPS limiters) cannot differentiate between a legitimate traffic spike "
        "(such as a popular news release) and an attack flood. Shannon Entropy calculates IP distribution diversity. "
        "A high volume spread across thousands of distinct users maintains high entropy, whereas an attack flood "
        "from a concentrated group of malicious sources drops entropy near zero, enabling highly accurate anomaly detection.", a_style
    ))

    # Q3
    story.append(Paragraph("Q: How does the system handle high-concurrency request checks without suffering from race conditions?", q_style))
    story.append(Paragraph(
        "A: Our telemetry trackers, sliding windows, and blacklist lists utilize thread-safe locks (`threading.Lock()`). "
        "By enforcing mutually exclusive access to shared states, we prevent concurrent socket handler threads from "
        "corrupting counters or misapplying rules.", a_style
    ))

    # Q4
    story.append(Paragraph("Q: Is this platform production-ready? What would you change for enterprise scale?", q_style))
    story.append(Paragraph(
        "A: This is an educational range. To deploy this at scale in production, we would: <br/>"
        "1. Offload IP blocking to kernel-level filters using **eBPF (Extended Berkeley Packet Filter)** or **XDP (eXpress Data Path)**.<br/>"
        "2. Replace in-memory dictionaries with **Redis** to synchronize blocklists across multiple server replicas.<br/>"
        "3. Transition the thread-per-connection pattern to an asynchronous event loop (e.g. `asyncio`) to handle millions of connections.", a_style
    ))

    # Doc compilation
    doc.build(story)
    print(f"Presentation PDF successfully built at: {output_path}")

if __name__ == '__main__':
    # Build the presentation guide in the ddos_platform root directory
    out_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_dest = os.path.join(out_dir, "DDoS_Project_Presentation_Guide.pdf")
    create_presentation_pdf(pdf_dest)
