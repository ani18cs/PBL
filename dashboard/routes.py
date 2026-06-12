from flask import Blueprint, render_template, jsonify, request, send_from_directory, redirect
import json
import os
import time
from database.models import ExperimentModel
from dashboard import state
from analytics.report_generator import REPORTS_DIR, generate_pdf_report

bp = Blueprint("dashboard", __name__, template_folder=None)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/mitigation")
def mitigation():
    return redirect("/")

@bp.route("/experiments")
def experiments():
    return render_template("experiments.html")

@bp.route("/api/logs", methods=["GET"])
def get_logs():
    return jsonify(state.log_buffer)

@bp.route("/api/experiments", methods=["GET"])
def get_experiments():
    try:
        exps = ExperimentModel.get_all()
        return jsonify(exps)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route("/api/experiments/start", methods=["POST"])
def start_exp():
    data = request.get_json() or {}
    name = data.get("name", "Unnamed Experiment")
    profile = data.get("profile", "normal")
    duration = int(data.get("duration", 30))
    
    if not state.experiment_runner:
        return jsonify({"status": "error", "message": "Experiment runner not initialized"}), 500
        
    success = state.experiment_runner.run_experiment(name, profile, duration)
    if success:
        state.active_experiment_name = name
        return jsonify({"status": "success", "message": f"Experiment '{name}' started."})
    return jsonify({"status": "error", "message": "An experiment is already active."}), 400

@bp.route("/api/experiments/stop", methods=["POST"])
def stop_exp():
    if not state.experiment_runner:
        return jsonify({"status": "error", "message": "Experiment runner not initialized"}), 500
        
    success = state.experiment_runner.stop_active_experiment()
    if success:
        state.active_experiment_name = None
        return jsonify({"status": "success", "message": "Experiment stopped."})
    return jsonify({"status": "error", "message": "No active experiment to stop."}), 400

@bp.route("/api/mitigation/block", methods=["POST"])
def block_ip():
    data = request.get_json() or {}
    ip = data.get("ip")
    duration = int(data.get("duration", 60))
    if not ip:
        return jsonify({"status": "error", "message": "Missing IP parameter"}), 400
        
    if not state.mitigation_controller:
        return jsonify({"status": "error", "message": "Mitigation controller not initialized"}), 500
        
    state.mitigation_controller.blacklist_manager.block_ip(ip, duration)
    return jsonify({"status": "success", "message": f"IP {ip} blocked for {duration} seconds."})

@bp.route("/api/mitigation/unblock", methods=["POST"])
def unblock_ip():
    data = request.get_json() or {}
    ip = data.get("ip")
    if not ip:
        return jsonify({"status": "error", "message": "Missing IP parameter"}), 400
        
    if not state.mitigation_controller:
        return jsonify({"status": "error", "message": "Mitigation controller not initialized"}), 500
        
    state.mitigation_controller.blacklist_manager.unblock_ip(ip)
    return jsonify({"status": "success", "message": f"IP {ip} unblocked."})

@bp.route("/api/mitigation/mode", methods=["POST"])
def change_mode():
    data = request.get_json() or {}
    mode = data.get("mode")
    if not mode:
        return jsonify({"status": "error", "message": "Missing mode parameter"}), 400
        
    if not state.mitigation_controller:
        return jsonify({"status": "error", "message": "Mitigation controller not initialized"}), 500
        
    success = state.mitigation_controller.set_mode(mode)
    if success:
        return jsonify({"status": "success", "message": f"Mode changed to {mode}."})
    return jsonify({"status": "error", "message": "Invalid mode option."}), 400

@bp.route("/api/reports", methods=["GET"])
def get_reports():
    try:
        if not os.path.exists(REPORTS_DIR):
            return jsonify([])
        files = [f for f in os.listdir(REPORTS_DIR) if f.endswith('.pdf')]
        reports = []
        for f in files:
            parts = f.split('_')
            exp_id = parts[1] if len(parts) >= 2 else "unknown"
            reports.append({
                "id": exp_id,
                "filename": f,
                "path": f"/api/reports/download/{exp_id}"
            })
        return jsonify(reports)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route("/api/reports/download/<int:exp_id>", methods=["GET"])
def download_report(exp_id):
    try:
        pdf_filename = f"experiment_{exp_id}_report.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        # Auto-compile PDF if not yet written
        if not os.path.exists(pdf_path):
            generate_pdf_report(exp_id)
            
        if not os.path.exists(pdf_path):
            return jsonify({"status": "error", "message": "Report file not found."}), 404
            
        return send_from_directory(REPORTS_DIR, pdf_filename, as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
