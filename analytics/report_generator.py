import os
import json
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from database.database import get_connection

REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"
)

def generate_pdf_report(experiment_id):
    """Generates an educational PDF report summarizing experiment logs and mitigation triggers."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Fetch Experiment
    cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
    exp = cursor.fetchone()
    if not exp:
        conn.close()
        return None
        
    exp = dict(exp)
    start_time = exp["start_time"]
    end_time = exp["end_time"] if exp["end_time"] else time.time()
    config = json.loads(exp["configuration"])
    
    # 2. Fetch Metrics
    cursor.execute(
        "SELECT * FROM system_metrics WHERE timestamp >= ? AND timestamp <= ?",
        (start_time, end_time)
    )
    sys_rows = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute(
        "SELECT * FROM traffic_metrics WHERE timestamp >= ? AND timestamp <= ?",
        (start_time, end_time)
    )
    traf_rows = [dict(r) for r in cursor.fetchall()]
    
    # 3. Fetch Alerts & Mitigations
    cursor.execute(
        "SELECT * FROM alerts WHERE timestamp >= ? AND timestamp <= ?",
        (start_time, end_time)
    )
    alerts = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute(
        "SELECT * FROM mitigation_actions WHERE timestamp >= ? AND timestamp <= ?",
        (start_time, end_time)
    )
    mitigations = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    
    # 4. Calculate key metrics summary
    max_cpu = max([r["cpu_usage"] for r in sys_rows]) if sys_rows else 0.0
    max_mem = max([r["memory_usage"] for r in sys_rows]) if sys_rows else 0.0
    max_pps = max([r["requests_per_second"] for r in traf_rows]) if traf_rows else 0
    max_conn = max([r["active_connections"] for r in traf_rows]) if traf_rows else 0
    avg_lat = (sum([r["average_latency"] for r in traf_rows]) / len(traf_rows)) if traf_rows else 0.0
    
    # Setup PDF path
    pdf_filename = f"experiment_{experiment_id}_report.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    
    # Build PDF flow elements
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#3b82f6'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )
    
    # Title
    story.append(Paragraph("🛡️ DEFCON-D Security Experiment Report", title_style))
    story.append(Paragraph(f"Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Spacer(1, 10))
    
    # Metadata table
    meta_data = [
        [Paragraph("<b>Attribute</b>", body_style), Paragraph("<b>Value</b>", body_style)],
        ["Experiment ID", str(exp["id"])],
        ["Experiment Name", exp["name"]],
        ["Traffic Profile", config.get("profile", "normal").upper()],
        ["Expected Duration", f"{config.get('duration')} seconds"],
        ["Virtual Clients count", str(config.get("clients"))],
        ["Request Throttling delay", f"{config.get('request_interval')}s"]
    ]
    t_meta = Table(meta_data, colWidths=[200, 300])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))
    
    # Stats table
    story.append(Paragraph("📊 Host Performance Metrics Summary", section_style))
    stats_data = [
        ["Peak CPU Usage", f"{max_cpu:.1f}%"],
        ["Peak Memory Usage", f"{max_mem:.1f}%"],
        ["Max Traffic Throughput", f"{max_pps} requests/sec"],
        ["Max Concurrent Sockets", f"{max_conn} connections"],
        ["Average Processing Latency", f"{avg_lat:.2f} ms"]
    ]
    t_stats = Table(stats_data, colWidths=[200, 300])
    t_stats.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 15))
    
    # Threat Alerts Table
    story.append(Paragraph("🚨 Security Alerts Logged", section_style))
    if not alerts:
        story.append(Paragraph("No security alerts triggered. Target system remained secure.", body_style))
    else:
        alert_rows = [[Paragraph("<b>Severity</b>", body_style), Paragraph("<b>Alert Details</b>", body_style), Paragraph("<b>Attacker IP</b>", body_style)]]
        for a in alerts:
            alert_rows.append([a["severity"], a["description"], a["source_ip"] if a["source_ip"] else 'N/A'])
        t_alerts = Table(alert_rows, colWidths=[100, 280, 120])
        t_alerts.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fee2e2')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(t_alerts)
    story.append(Spacer(1, 15))
    
    # Mitigation Table
    story.append(Paragraph("🛡️ Mitigation Actions Deployed", section_style))
    if not mitigations:
        story.append(Paragraph("No mitigation overrides triggered during simulation window.", body_style))
    else:
        mit_rows = [[Paragraph("<b>Action Type</b>", body_style), Paragraph("<b>Target IP</b>", body_style), Paragraph("<b>Block Timer</b>", body_style)]]
        for m in mitigations:
            mit_rows.append([m["action"], m["target"], f"{m['duration']}s" if m["duration"] else 'Permanent'])
        t_mits = Table(mit_rows, colWidths=[150, 200, 150])
        t_mits.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d1fae5')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#a7f3d0')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(t_mits)
    story.append(Spacer(1, 15))

    # Educational Conclusion
    story.append(Paragraph("📝 Experiment Conclusion & Defensive Action Summary", section_style))
    conclusion_text = (
        "Based on collected metrics, the platform has successfully simulated client connections. "
        "Under elevated loading (Medium/Heavy profiles), request frequency and latency spikes trigger "
        "the anomaly engines. In Automatic defense mode, the mitigation systems successfully logged rate-limit "
        "offenses and temporary blacklist overrides to SQLite database, blocking the targeted flows. "
        "This experiment confirms the effectiveness of multi-tiered rate limiting and signature alerts in DDoS mitigation."
    )
    story.append(Paragraph(conclusion_text, body_style))
    
    doc.build(story)
    print(f"[ReportGenerator] Report PDF generated successfully: {pdf_path}")
    return pdf_path
