# -*- coding: utf-8 -*-
"""
pipeline_viz.py — 시연용 파이프라인 시각화 모듈
1) 노트북 내장 SVG 다이어그램: 셀 실행에 따라 in-place 갱신
2) pipeline_status.json 기록 → pipeline_dashboard.html 이 폴링하여
   단계 상태 + 결과물(표 미리보기, 그림)을 함께 표시
"""
import json
import time
import threading
import http.server
from pathlib import Path
from IPython.display import display, HTML

STATUS_FILE = Path("pipeline_status.json")
DIAGRAM_PATH = "docs/pipeline_architecture.diagram.ko.html"

COLORS = {
    "pending": ("#e2e8f0", "#64748b"),
    "running": ("#fef3c7", "#b45309"),
    "done":    ("#dcfce7", "#15803d"),
    "error":   ("#fee2e2", "#b91c1c"),
}
ICONS = {"pending": "○", "running": "▶", "done": "✔", "error": "✖"}


class PipelineViz:
    def __init__(self, stages):
        """stages: [(key, 표시이름, 설명), ...]"""
        self.stages = [
            {"key": k, "name": n, "desc": d, "status": "pending",
             "detail": "", "elapsed": None, "artifacts": [], "_t0": None}
            for k, n, d in stages
        ]
        self._handle = None
        self._write_status()
        self._handle = display(HTML(self._svg()), display_id=True)

    # ---------- 상태 제어 ----------
    def _get(self, key):
        return next(s for s in self.stages if s["key"] == key)

    def start(self, key, detail=""):
        s = self._get(key)
        s.update(status="running", detail=detail, _t0=time.time())
        s["artifacts"] = []
        self._refresh()

    def update(self, key, detail):
        self._get(key)["detail"] = detail
        self._refresh()

    def done(self, key, detail=""):
        s = self._get(key)
        s["status"] = "done"
        if detail:
            s["detail"] = detail
        if s["_t0"]:
            s["elapsed"] = round(time.time() - s["_t0"], 1)
        self._refresh()

    def error(self, key, detail=""):
        s = self._get(key)
        s.update(status="error", detail=detail)
        self._refresh()

    def reset(self):
        for s in self.stages:
            s.update(status="pending", detail="", elapsed=None, _t0=None, artifacts=[])
        self._refresh()

    # ---------- 결과물 기록 (대시보드에 표시) ----------
    def log_table(self, key, df, title, max_rows=8):
        """DataFrame 미리보기를 대시보드에 표시"""
        html = df.head(max_rows).to_html(index=False, border=0, na_rep="")
        self._get(key)["artifacts"].append(
            {"type": "table", "title": f"{title}  ({len(df):,} rows)", "html": html})
        self._refresh()

    def log_image(self, key, path, title=""):
        """이미지 파일(figures/*.png 등)을 대시보드에 표시 (프로젝트 루트 기준 상대경로)"""
        self._get(key)["artifacts"].append(
            {"type": "image", "title": title or Path(path).name, "path": str(path)})
        self._refresh()

    def log_text(self, key, text, title=""):
        self._get(key)["artifacts"].append(
            {"type": "text", "title": title, "html": f"<pre>{text}</pre>"})
        self._refresh()

    def _refresh(self):
        self._write_status()
        if self._handle:
            self._handle.update(HTML(self._svg()))

    # ---------- 대시보드용 상태 파일 ----------
    def _write_status(self):
        data = {
            "updated": time.strftime("%H:%M:%S"),
            "stages": [{k: v for k, v in s.items() if not k.startswith("_")}
                       for s in self.stages],
        }
        STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # ---------- 노트북 내장 SVG ----------
    def _svg(self):
        n = len(self.stages)
        bw, bh, gap, pad = 240, 96, 70, 16
        width = pad * 2 + bw * n + gap * (n - 1)
        height = bh + pad * 2 + 26
        parts = [
            f'<svg width="{width}" height="{height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'style="font-family:Pretendard,\'Malgun Gothic\',sans-serif">'
        ]
        for i, s in enumerate(self.stages):
            x = pad + i * (bw + gap)
            fill, tcol = COLORS[s["status"]]
            pulse = ("<animate attributeName='opacity' values='1;0.55;1' "
                     "dur='1.2s' repeatCount='indefinite'/>") if s["status"] == "running" else ""
            parts.append(
                f'<rect x="{x}" y="{pad}" width="{bw}" height="{bh}" rx="14" '
                f'fill="{fill}" stroke="{tcol}" stroke-width="2">{pulse}</rect>'
                f'<text x="{x+16}" y="{pad+30}" font-size="16" font-weight="700" '
                f'fill="{tcol}">{ICONS[s["status"]]} {s["name"]}</text>'
                f'<text x="{x+16}" y="{pad+52}" font-size="12" fill="#475569">{s["desc"]}</text>'
                f'<text x="{x+16}" y="{pad+74}" font-size="12" fill="{tcol}">{s["detail"][:34]}</text>'
            )
            if s["elapsed"] is not None:
                parts.append(
                    f'<text x="{x+bw-14}" y="{pad+bh+18}" font-size="11" '
                    f'text-anchor="end" fill="#94a3b8">{s["elapsed"]}s</text>')
            if i < n - 1:
                ax0, ax1 = x + bw, x + bw + gap
                ay = pad + bh / 2
                acol = "#22c55e" if s["status"] == "done" else "#cbd5e1"
                parts.append(
                    f'<line x1="{ax0+6}" y1="{ay}" x2="{ax1-12}" y2="{ay}" '
                    f'stroke="{acol}" stroke-width="3"/>'
                    f'<polygon points="{ax1-12},{ay-7} {ax1-12},{ay+7} {ax1-2},{ay}" fill="{acol}"/>')
        parts.append("</svg>")
        return "".join(parts)


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):  # 접근 로그 출력 안 함
        pass


_server = None  # 중복 실행 방지


def start_dashboard(port=8765, directory="."):
    """백그라운드 HTTP 서버 실행 (접근 로그 없음) → 브라우저에서 대시보드 열기.
    셀을 다시 실행해도 에러 없이 동작 (이미 떠 있으면 재사용, 포트 충돌 시 다음 포트 시도)."""
    global _server
    import functools
    if _server is not None:                     # 같은 커널에서 재실행
        port = _server.server_address[1]
    else:
        handler = functools.partial(_QuietHandler, directory=directory)
        for p in range(port, port + 10):
            try:
                _server = http.server.ThreadingHTTPServer(("127.0.0.1", p), handler)
                port = p
                break
            except OSError:                     # 포트 사용 중 → 다음 포트
                continue
        else:
            print(f"포트 {port}~{port+9} 모두 사용 중 — 이미 실행된 대시보드가 있는지 확인하세요.")
            return f"http://127.0.0.1:{port}/pipeline_dashboard.html"
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/pipeline_dashboard.html"
    print(f"대시보드: {url}")
    return url


def show_diagram(height=520):
    """대시보드와 같은 구조 다이어그램을 노트북 셀 출력에 띄운다.

    start_dashboard() 로 띄운 로컬 서버를 통해 불러온다. 서버가 없으면
    안내만 출력한다 (다이어그램 파일 자체는 브라우저로 직접 열어도 동작)."""
    from IPython.display import IFrame

    if _server is None:
        print(f"start_dashboard() 를 먼저 실행하세요. 파일: {DIAGRAM_PATH}")
        return None
    port = _server.server_address[1]
    return IFrame(f"http://127.0.0.1:{port}/{DIAGRAM_PATH}", width="100%", height=height)
