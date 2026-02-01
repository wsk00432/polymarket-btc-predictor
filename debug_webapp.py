#!/usr/bin/env python3
"""
Debug version of webapp.py to identify the database path issue.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import io
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field, ValidationError, field_validator

# Import from the project
import sys
sys.path.insert(0, '/root/clawd/binance-oi-spike-radar-clone')

from src.config import default_config
from src.radar_service import run_radar
from src.state import app_state


BASE_DIR = Path('/root/clawd/binance-oi-spike-radar-clone/src')
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

_radar_task: Optional[asyncio.Task] = None
_DEFAULTS = default_config()


class ConfigModel(BaseModel):
    BASE_URL: str = Field(default=_DEFAULTS["BASE_URL"], min_length=1)
    ASSET_PRODUCT_URL: str = Field(default=_DEFAULTS["ASSET_PRODUCT_URL"], min_length=1)
    KLINE_INTERVAL: str = Field(default=_DEFAULTS["KLINE_INTERVAL"], min_length=1)
    KLINE_LIMIT: int = Field(default=_DEFAULTS["KLINE_LIMIT"], ge=1, le=1000)
    KLINE_SOURCE: str = Field(default=_DEFAULTS["KLINE_SOURCE"], min_length=1)
    KLINE_CONFIRM_BARS: int = Field(default=_DEFAULTS["KLINE_CONFIRM_BARS"], ge=0, le=20)
    CHART_WINDOW: int = Field(default=_DEFAULTS["CHART_WINDOW"], ge=10, le=200)
    ENABLE_BACKTEST: bool = Field(default=_DEFAULTS["ENABLE_BACKTEST"])
    ALERT_STORE_PATH: str = Field(default=_DEFAULTS["ALERT_STORE_PATH"], min_length=1)
    ALERT_RETENTION_DAYS: int = Field(default=_DEFAULTS["ALERT_RETENTION_DAYS"], ge=1, le=365)
    ALERT_MAX_RECORDS: int = Field(default=_DEFAULTS["ALERT_MAX_RECORDS"], ge=1, le=50000)
    SMA_PERIOD: int = Field(default=_DEFAULTS["SMA_PERIOD"], ge=2, le=200)
    ATR_PERIOD: int = Field(default=_DEFAULTS["ATR_PERIOD"], ge=2, le=200)
    RET_STD_PERIOD: int = Field(default=_DEFAULTS["RET_STD_PERIOD"], ge=2, le=200)
    OI_ZSCORE_PERIOD: int = Field(default=_DEFAULTS["OI_ZSCORE_PERIOD"], ge=2, le=200)
    LIQUIDITY_WINDOW: int = Field(default=_DEFAULTS["LIQUIDITY_WINDOW"], ge=2, le=200)
    SWING_LOOKBACK: int = Field(default=_DEFAULTS["SWING_LOOKBACK"], ge=2, le=200)
    PRICE_1H_CHANGE_BARS: int = Field(default=_DEFAULTS["PRICE_1H_CHANGE_BARS"], ge=2, le=60)
    PRICE_1H_TIER1: float = Field(default=_DEFAULTS["PRICE_1H_TIER1"], ge=0.0, le=1.0)
    PRICE_1H_TIER2: float = Field(default=_DEFAULTS["PRICE_1H_TIER2"], ge=0.0, le=1.0)
    PRICE_1H_TIER3: float = Field(default=_DEFAULTS["PRICE_1H_TIER3"], ge=0.0, le=1.0)
    PRICE_24H_CHANGE_MIN: float = Field(default=_DEFAULTS["PRICE_24H_CHANGE_MIN"], ge=0.0, le=1.0)
    VOL_MULTIPLIER: float = Field(default=_DEFAULTS["VOL_MULTIPLIER"], ge=0.1, le=20.0)
    VOL_NEXT_BOOST: float = Field(default=_DEFAULTS["VOL_NEXT_BOOST"], ge=0.1, le=20.0)
    PRICE_ATR_THRESHOLD: float = Field(default=_DEFAULTS["PRICE_ATR_THRESHOLD"], ge=0.1, le=20.0)
    RET_STD_MULTIPLIER: float = Field(default=_DEFAULTS["RET_STD_MULTIPLIER"], ge=0.1, le=20.0)
    PRICE_1H_CHANGE_THRESHOLD: float = Field(default=_DEFAULTS["PRICE_1H_CHANGE_THRESHOLD"], ge=0.0, le=1.0)
    OI_CHANGE_PCT_THRESHOLD: float = Field(default=_DEFAULTS["OI_CHANGE_PCT_THRESHOLD"], ge=0.0, le=1.0)
    OI_ZSCORE_THRESHOLD: float = Field(default=_DEFAULTS["OI_ZSCORE_THRESHOLD"], ge=0.0, le=20.0)
    OI_CHANGE_STRONG_THRESHOLD: float = Field(default=_DEFAULTS["OI_CHANGE_STRONG_THRESHOLD"], ge=0.0, le=1.0)
    W_VOL: float = Field(default=_DEFAULTS["W_VOL"], ge=0.0, le=10.0)
    W_PRICE: float = Field(default=_DEFAULTS["W_PRICE"], ge=0.0, le=10.0)
    W_PRICE_1H: float = Field(default=_DEFAULTS["W_PRICE_1H"], ge=0.0, le=10.0)
    W_OI: float = Field(default=_DEFAULTS["W_OI"], ge=0.0, le=10.0)
    W_OI_STRONG: float = Field(default=_DEFAULTS["W_OI_STRONG"], ge=0.0, le=10.0)
    SCORE_THRESHOLD: float = Field(default=_DEFAULTS["SCORE_THRESHOLD"], ge=0.0, le=10.0)
    REQUIRE_PRICE_1H_CHANGE: bool = Field(default=_DEFAULTS["REQUIRE_PRICE_1H_CHANGE"])
    ALERT_FILTER_MODE: str = Field(default=_DEFAULTS["ALERT_FILTER_MODE"], min_length=1)
    SCAN_INTERVAL_SEC: int = Field(default=_DEFAULTS["SCAN_INTERVAL_SEC"], ge=1, le=3600)
    MAX_CONCURRENCY: int = Field(default=_DEFAULTS["MAX_CONCURRENCY"], ge=1, le=200)
    MIN_REQUEST_INTERVAL_SEC: float = Field(default=_DEFAULTS["MIN_REQUEST_INTERVAL_SEC"], ge=0.0, le=10.0)
    RETRY_TIMES: int = Field(default=_DEFAULTS["RETRY_TIMES"], ge=0, le=10)
    RETRY_BACKOFF_SEC: float = Field(default=_DEFAULTS["RETRY_BACKOFF_SEC"], ge=0.0, le=10.0)
    TIMEOUT_SEC: int = Field(default=_DEFAULTS["TIMEOUT_SEC"], ge=1, le=120)
    TOP_N_SYMBOLS: int = Field(default=_DEFAULTS["TOP_N_SYMBOLS"], ge=0, le=500)
    CHART_VERDICT_URL: str = Field(default=_DEFAULTS["CHART_VERDICT_URL"])
    CHART_VERDICT_TIMEOUT_SEC: int = Field(default=_DEFAULTS["CHART_VERDICT_TIMEOUT_SEC"], ge=1, le=120)
    PRINT_CONSOLE_LOGS: bool = Field(default=_DEFAULTS["PRINT_CONSOLE_LOGS"])

    @field_validator("TOP_N_SYMBOLS", mode="before")
    @classmethod
    def _coerce_top_n(cls, value):
        if value is None or value == "":
            return 0
        return value

    @field_validator("KLINE_SOURCE", mode="before")
    @classmethod
    def _coerce_kline_source(cls, value):
        if value is None or value == "":
            return "trade"
        return value


def _setup_logging() -> None:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    from src.state import WebLogHandler
    web_handler = WebLogHandler(app_state)
    web_handler.setFormatter(formatter)
    root_logger.addHandler(web_handler)

    if app_state.config.get("PRINT_CONSOLE_LOGS", True):
        has_stream = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
        if not has_stream:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            root_logger.addHandler(stream_handler)


@app.on_event("startup")
async def on_startup() -> None:
    global _radar_task
    _setup_logging()
    await app_state.load_config_from_file()
    
    try:
        normalized = ConfigModel.model_validate(app_state.config)
    except ValidationError:
        normalized = ConfigModel()
    await app_state.set_config(normalized.model_dump())
    
    # DEBUG: Print the alert store path before loading
    print(f"DEBUG: ALERT_STORE_PATH from config: {app_state.config.get('ALERT_STORE_PATH')}")
    print(f"DEBUG: ALERT_STORE_PATH from app_state: {app_state.alert_store_path}")
    
    # Load alerts from store
    app_state.load_alerts_from_store()
    _radar_task = asyncio.create_task(run_radar(app_state))


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global _radar_task
    if _radar_task:
        _radar_task.cancel()
        try:
            await _radar_task
        except asyncio.CancelledError:
            pass


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/status")
async def get_status() -> Dict[str, Any]:
    return app_state.get_status()


@app.get("/api/symbols")
async def get_symbols() -> Dict[str, Any]:
    symbols = app_state.get_symbols()
    return {"symbols": symbols, "count": len(symbols)}


@app.get("/api/config")
async def get_config() -> Dict[str, Any]:
    return app_state.config


@app.post("/api/config")
async def update_config(payload: ConfigModel) -> Dict[str, Any]:
    data = payload.model_dump()
    return await app_state.set_config(data)


@app.post("/api/config/reset")
async def reset_config() -> Dict[str, Any]:
    return await app_state.reset_config()


@app.get("/api/alert/{alert_id}")
async def get_alert(alert_id: str) -> Dict[str, Any]:
    alert = app_state.get_alert(alert_id)
    if not alert:
        return {"alert": None, "stats": {}}
    alert_view = dict(alert)
    alert_view.pop("chart_klines", None)
    return {
        "alert": alert_view,
        "stats_summary": alert.get("stats_summary", {}),
    }


@app.get("/api/alert/{alert_id}/chart")
async def get_alert_chart(alert_id: str) -> Response:
    alert = app_state.get_alert(alert_id)
    if not alert:
        return Response(status_code=404)
    klines = alert.get("chart_klines") or []
    if not klines:
        return Response(status_code=404)
    marker_index = alert.get("first_trigger_candle_index")
    png_bytes = _render_candles_png(klines, marker_index)
    return Response(content=png_bytes, media_type="image/png")


@app.get("/api/alerts")
async def get_alerts() -> Dict[str, Any]:
    return {"alerts": app_state.get_alerts()}


@app.websocket("/ws/logs")
async def ws_logs(websocket: WebSocket) -> None:
    await websocket.accept()
    app_state.log_sockets.add(websocket)
    for item in list(app_state.logs):
        await websocket.send_json(item)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        app_state.log_sockets.discard(websocket)


@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket) -> None:
    await websocket.accept()
    app_state.alert_sockets.add(websocket)
    for item in list(app_state.alerts):
        await websocket.send_json(item)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        app_state.alert_sockets.discard(websocket)


def _render_candles_png(klines, marker_index: Optional[int]) -> bytes:
    opens = [float(k[1]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]

    fig, (ax, ax_vol) = plt.subplots(
        2, 1, figsize=(6, 5.2), gridspec_kw={"height_ratios": [3.4, 1.6], "hspace": 0.05}
    )
    ax.set_facecolor("#0f141d")
    ax_vol.set_facecolor("#0f141d")
    fig.patch.set_facecolor("#0f141d")

    width = 0.6
    kline_up = "#35d07f"
    kline_down = "#ff5c6c"
    vol_up = "#4caf50"
    vol_down = "#ef5350"
    min_low = min(lows) if lows else 0.0
    max_high = max(highs) if highs else 0.0
    max_vol = max(volumes) if volumes else 0.0
    for i in range(len(closes)):
        kline_color = kline_up if closes[i] >= opens[i] else kline_down
        vol_color = vol_up if closes[i] >= opens[i] else vol_down
        ax.vlines(i, lows[i], highs[i], color=kline_color, linewidth=0.8)
        lower = min(opens[i], closes[i])
        height = abs(closes[i] - opens[i]) or 0.0001
        ax.add_patch(plt.Rectangle((i - width / 2, lower), width, height, color=kline_color))
        ax_vol.bar(
            i,
            volumes[i],
            color=vol_color,
            alpha=0.18,
            width=0.8,
            edgecolor=vol_color,
            linewidth=0.6,
        )

    if isinstance(marker_index, int) and 0 <= marker_index < len(volumes) and max_vol > 0:
        start_idx = max(0, marker_index - 2)
        labels = []
        for i in range(start_idx, marker_index + 1):
            value = volumes[i]
            if value >= 1e9:
                label = f"{value / 1e9:.2f}B"
            elif value >= 1e6:
                label = f"{value / 1e6:.2f}M"
            elif value >= 1e3:
                label = f"{value / 1e3:.2f}K"
            else:
                label = f"{value:.0f}"
            labels.append(label)
        label_text = "   ".join(labels)
        ax_vol.text(
            len(closes) - 0.3,
            -max_vol * 0.08,
            label_text,
            ha="right",
            va="top",
            fontsize=9,
            color="#ffffff",
        )

    if closes:
        ax.set_xlim(-0.7, len(closes) - 0.3)
        ax_vol.set_xlim(-0.7, len(closes) - 0.3)
    if max_high > min_low:
        pad = (max_high - min_low) * 0.04
        ax.set_ylim(min_low - pad, max_high + pad)
    ax.margins(0)
    ax_vol.margins(0)
    if max_vol > 0:
        ax_vol.set_ylim(bottom=-max_vol * 0.18, top=max_vol * 1.05)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.98, bottom=0.06, hspace=0.05)

    if isinstance(marker_index, int) and 0 <= marker_index < len(closes):
        ax.axvline(marker_index, color="#f6c453", linestyle="--", linewidth=0.6, alpha=0.6)
        ax_vol.axvline(marker_index, color="#f6c453", linestyle="--", linewidth=0.6, alpha=0.6)

    ax.set_xticks([])
    ax.set_yticks([])
    ax_vol.set_xticks([])
    ax_vol.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in ax_vol.spines.values():
        spine.set_visible(False)
    fig.tight_layout(pad=0.2)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("debug_webapp:app", host="0.0.0.0", port=8000, reload=False)