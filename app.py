import io
from collections import Counter
from datetime import datetime
from pathlib import Path
 
import streamlit as st
from PIL import Image
from ultralytics import YOLO
 
# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="GreenGuard | Weed Detection",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ---------------- ATTRACTIVE GREEN THEME ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
 
html, body, [class*="css"], .stApp {
    font-family: 'Poppins', sans-serif;
}
 
.stApp {
    background: linear-gradient(135deg, #f0fae9 0%, #e0f2d5 45%, #c6e6b5 100%);
    color: #23452a;
}
 
[data-testid="stHeader"] { background: rgba(237, 248, 232, 0.95); }
 
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #174b2b, #286b3d);
}
[data-testid="stSidebar"] * { color: #ffffff !important; }
 
/* ---------- Hero ---------- */
.hero {
    background:
        linear-gradient(100deg, rgba(14, 55, 28, 0.92) 0%,
                                rgba(30, 100, 50, 0.72) 55%,
                                rgba(60, 140, 70, 0.35) 100%),
        url('https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=1800&q=80')
        center / cover no-repeat,
        linear-gradient(120deg, #174b2b, #39864a);
    padding: 64px 44px;
    border-radius: 26px;
    margin-bottom: 22px;
    box-shadow: 0 14px 34px rgba(25, 80, 35, 0.28);
    position: relative;
    overflow: hidden;
}
.hero h1 {
    color: #ffffff !important;
    font-size: 3.2rem;
    font-weight: 700;
    margin-bottom: 8px;
    text-shadow: 0 3px 12px rgba(0, 0, 0, 0.35);
}
.hero p  { color: #f1ffe9 !important; font-size: 1.1rem; max-width: 640px; }
 
.badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(6px);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.4);
    padding: 5px 16px;
    border-radius: 999px;
    font-size: 0.84rem;
    margin: 8px 8px 0 0;
}
 
/* ---------- Crop field photo (green gradient is the fallback) ---------- */
.field-photo {
    height: 380px;
    border-radius: 24px;
    margin-bottom: 22px;
    border: 1px solid #9ccf86;
    box-shadow: 0 12px 30px rgba(40, 100, 40, 0.22);
    position: relative;
    overflow: hidden;
    background:
        url('https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=1800&h=700&q=85')
        center / cover no-repeat,
        url('https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1800&h=700&q=85')
        center / cover no-repeat,
        url('https://images.unsplash.com/photo-1471193945509-9ad0617afabf?auto=format&fit=crop&w=1800&h=700&q=85')
        center / cover no-repeat,
        linear-gradient(180deg, #bfe8f5, #4f9d3f);
}
.field-overlay {
    position: absolute;
    inset: auto 0 0 0;
    padding: 70px 32px 26px 32px;
    background: linear-gradient(0deg, rgba(10, 45, 22, 0.88), rgba(10, 45, 22, 0));
}
.field-overlay h2 {
    color: #ffffff !important;
    margin: 0 0 4px 0;
    font-size: 1.7rem;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
}
.field-overlay p { color: #e8ffd9 !important; margin: 0; }
@media (max-width: 640px) { .field-photo { height: 260px; } }
 
h1, h2, h3 { color: #245c32; }
 
/* ---------- Cards ---------- */
.section-card {
    background: linear-gradient(160deg, #ffffff 0%, #f1fbe9 100%);
    padding: 24px;
    border-radius: 20px;
    border: 1px solid #b9dca9;
    border-top: 6px solid #64b947;
    height: 200px;                 /* same height for all three cards */
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    box-shadow: 0 4px 12px rgba(40, 100, 40, 0.08);
    transition: transform .2s ease, box-shadow .2s ease;
}
.section-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 22px rgba(40, 100, 40, 0.16);
}
.card-icon {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: linear-gradient(135deg, #64b947, #b6e79a);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    margin-bottom: 12px;
}
.section-card h3 { margin: 0 0 6px 0 !important; font-size: 1.2rem; }
.section-card p  { margin: 0; line-height: 1.5; }
.section-card h3 { color: #28723b !important; }
.section-card p  { color: #365b3a !important; }
 
/* ---------- Steps ---------- */
.step {
    background: #ffffff;
    border-left: 6px solid #64b947;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 3px 10px rgba(40, 100, 40, 0.07);
}
.step b { color: #245c32; }
 
/* ---------- Result banner ---------- */
.result-banner {
    background: linear-gradient(100deg, #ffffff, #eaf8e0);
    border: 1px solid #9ccf86;
    border-radius: 18px;
    padding: 18px 24px;
    margin: 10px 0 18px 0;
}
.result-banner h3 { margin: 0; }
 
/* ---------- Buttons ---------- */
div.stButton > button, div.stDownloadButton > button {
    background: linear-gradient(100deg, #64b947, #a4df80);
    color: #173e20;
    border: 1px solid #69b94e;
    border-radius: 12px;
    min-height: 48px;
    font-weight: bold;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: #c4efac;
    color: #174b2b;
    border: 1px solid #4e9c3d;
}
 
/* ---------- Widgets ---------- */
[data-testid="stFileUploader"] {
    background: #f8fff4;
    padding: 16px;
    border: 1px dashed #67a954;
    border-radius: 15px;
}
[data-testid="stFileUploader"] * { color: #23452a; }
 
[data-testid="stMetric"] {
    background: #ffffff;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #b9dca9;
    box-shadow: 0 3px 10px rgba(40, 100, 40, 0.06);
}
 
[data-testid="stAlert"] { border-radius: 12px; }
 
[data-baseweb="tab-list"] { gap: 8px; }
button[data-baseweb="tab"] {
    background: #ffffff;
    border-radius: 12px 12px 0 0;
    padding: 8px 18px;
}
[data-testid="stExpander"] {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #b9dca9;
}
 
hr { border-color: #b2d5a2; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
 
 
# ---------------- MODEL LOCATION ----------------
# best.pt must be in the same folder as this file.
MODEL_PATH = Path(__file__).resolve().parent / "best.pt"
 
 
@st.cache_resource
def load_model(model_path):
    return YOLO(str(model_path))
 
 
def image_to_png_bytes(array_rgb):
    buffer = io.BytesIO()
    Image.fromarray(array_rgb).save(buffer, format="PNG")
    return buffer.getvalue()
 
 
# ---------------- SESSION DEFAULTS ----------------
if "history" not in st.session_state:
    st.session_state["history"] = []
 
 
# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("# 🌿 GreenGuard")
    st.write("SMART AGRICULTURE SYSTEM")
    st.divider()
 
    st.markdown("### 🌱 Project Menu")
    st.write("🏠 Home")
    st.write("🔍 Weed Detection")
    st.write("🌾 Weed Management")
 
    st.divider()
 
    st.markdown("### ⚙️ Detection Settings")
    conf_value = st.slider(
        "Confidence threshold", 0.01, 0.90, 0.05, 0.01,
        help="Lower = more detections (and more false alarms). "
             "Higher = fewer, more certain detections.",
    )
    img_size = st.select_slider(
        "Image size", options=[320, 480, 640, 800, 960], value=640,
        help="Larger sizes can find smaller weeds but run slower.",
    )
    max_detections = st.slider("Maximum detections", 1, 50, 10)
 
    st.divider()
 
    st.markdown("### 🕘 Session")
    st.metric("Images analysed", len(st.session_state["history"]))
 
    if st.session_state["history"]:
        if st.button("Clear history", use_container_width=True):
            st.session_state["history"] = []
            st.rerun()
 
    st.divider()
    st.caption("Deep Learning • YOLOv8")
 
 
# ---------------- HERO BANNER ----------------
st.markdown("""
<div class="hero">
    <h1>🌿 GreenGuard</h1>
    <p><b>Intelligent Weed Detection in Crop Fields</b></p>
    <p>Identify potential weeds using deep learning and support
    healthier crop growth with smart agriculture.</p>
    <span class="badge">🤖 YOLOv8</span>
    <span class="badge">⚡ Instant results</span>
    <span class="badge">🌾 Crop-field ready</span>
</div>
""", unsafe_allow_html=True)
 
 
# ---------------- QUICK STATS ----------------
s1, s2, s3, s4 = st.columns(4, gap="medium")
s1.metric("🧠 Model", "YOLOv8")
s2.metric("🖼️ Input", "JPG / PNG")
s3.metric("📐 Image size", f"{img_size}px")
s4.metric("🎯 Confidence", f"{conf_value:.2f}")
 
st.write("")
 
# ---------------- INFO TABS ----------------
tab_home, tab_how, tab_manage, tab_faq = st.tabs(
    ["🌱 Overview", "🛠️ How It Works", "🌾 Weed Management", "❓ FAQ"]
)
 
with tab_home:
    st.markdown("## 🌱 Welcome to Smart Farming")
    st.write(
        "Upload a crop-field photograph and let the trained YOLOv8 model "
        "analyse it. View the detection results and explore practical "
        "weed-management methods."
    )
 
    st.markdown(
        '''<div class="field-photo">
<div class="field-overlay">
<h2>Protect every plant, grow a greener harvest</h2>
<p>Detect weeds early and keep your fields healthy and productive.</p>
</div></div>''',
        unsafe_allow_html=True,
    )
 
    st.markdown("## ✨ Project Features")
    card1, card2, card3 = st.columns(3, gap="medium")
 
    with card1:
        st.markdown("""
        <div class="section-card">
            <div class="card-icon">📷</div>
            <h3>Image Upload</h3>
            <p>Upload a crop-field image for analysis.</p>
        </div>
        """, unsafe_allow_html=True)
 
    with card2:
        st.markdown("""
        <div class="section-card">
            <div class="card-icon">🔍</div>
            <h3>AI Detection</h3>
            <p>Find weeds with the trained YOLOv8 model.</p>
        </div>
        """, unsafe_allow_html=True)
 
    with card3:
        st.markdown("""
        <div class="section-card">
            <div class="card-icon">🌾</div>
            <h3>Weed Management</h3>
            <p>Explore ways to control unwanted plants.</p>
        </div>
        """, unsafe_allow_html=True)
 
with tab_how:
    st.markdown("## 🛠️ How GreenGuard Works")
    st.markdown("""
    <div class="step"><b>Step 1 · Upload</b><br>
    Choose a clear photo of your crop field (JPG or PNG).</div>
    <div class="step"><b>Step 2 · Analyse</b><br>
    The YOLOv8 model scans the image and finds objects it recognises as
    weeds.</div>
    <div class="step"><b>Step 3 · Review</b><br>
    Compare the original and the detected image, and check the confidence
    of each detection.</div>
    <div class="step"><b>Step 4 · Act</b><br>
    Download the result and use the weed-management tips to protect your crop.</div>
    """, unsafe_allow_html=True)
 
with tab_manage:
    st.markdown("## 🌾 Weed Management Methods")
    with st.expander("🧑‍🌾 Manual weeding"):
        st.write("Hand pulling or hoeing works well on small fields and young "
                 "weeds. Remove the whole root so the weed does not regrow.")
    with st.expander("🌿 Mulching"):
        st.write("A layer of straw, leaves or plastic sheet blocks sunlight and "
                 "stops weed seeds from germinating.")
    with st.expander("🔄 Crop rotation"):
        st.write("Changing crops each season breaks the life cycle of weeds "
                 "that prefer one particular crop.")
    with st.expander("🧪 Targeted herbicide"):
        st.write("Spot-spray only where weeds are detected, using the "
                 "recommended dose. This saves money and reduces damage to "
                 "soil and crops.")
 
with tab_faq:
    st.markdown("## ❓ Frequently Asked Questions")
    with st.expander("What image works best?"):
        st.write("A sharp, well-lit photo taken from above or at a slight "
                 "angle, where plants are clearly visible.")
    with st.expander("What does the confidence score mean?"):
        st.write("It is how sure the model is about a detection, from 0 to 1. "
                 "Higher means more certain.")
    with st.expander("Why are some weeds missed?"):
        st.write("Small, hidden or blurry weeds can be missed. Try a clearer "
                 "image, a larger image size, or a lower confidence threshold.")
 
st.divider()
 
 
# ---------------- IMAGE UPLOAD ----------------
st.markdown("## 📤 Upload Your Crop Image")
 
uploaded_file = st.file_uploader(
    "Choose a crop-field image",
    type=["jpg", "jpeg", "png"],
    help="Select a clear image showing crops or weeds.",
)
 
 
# ---------------- WEED DETECTION ----------------
if uploaded_file is not None:
 
    image = Image.open(uploaded_file).convert("RGB")
 
    info1, info2, info3 = st.columns(3)
    info1.metric("📁 File", uploaded_file.name[:18])
    info2.metric("📏 Resolution", f"{image.width} × {image.height}")
    info3.metric("💾 Size", f"{uploaded_file.size / 1024:.0f} KB")
 
    st.markdown("### 🖼️ Selected Image")
    st.image(image, caption="Your uploaded crop-field image",
             use_container_width=True)
 
    if st.button("🌿 Detect Weeds", type="primary", use_container_width=True):
 
        if not MODEL_PATH.is_file():
            st.error(f"Model file not found: {MODEL_PATH}")
            st.stop()
 
        try:
            progress = st.progress(0, text="Loading model...")
 
            model = load_model(str(MODEL_PATH))
            progress.progress(35, text="Analysing your image...")
 
            # Only draw the weed class, so crop plants are never boxed.
            weed_ids = [i for i, n in model.names.items()
                        if "weed" in str(n).lower()]
 
            result = model.predict(
                source=image,
                imgsz=img_size,
                conf=conf_value,
                max_det=max_detections,
                classes=weed_ids or None,
                verbose=False,
            )[0]
            progress.progress(80, text="Drawing detections...")
 
            predictions = []
            for box in result.boxes:
                class_id = int(box.cls[0])
                predictions.append({
                    "class": str(model.names[class_id]),
                    "confidence": round(float(box.conf[0]), 3),
                })
 
            detected_bgr = result.plot()
            detected_rgb = detected_bgr[:, :, ::-1].copy()
 
            st.session_state["original_image"] = image
            st.session_state["detected_image"] = detected_rgb
            st.session_state["predictions"] = predictions
            st.session_state["box_count"] = len(result.boxes)
 
            st.session_state["history"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "file": uploaded_file.name,
                "detections": len(result.boxes),
            })
 
            progress.progress(100, text="Done!")
            progress.empty()
 
        except Exception as error:
            st.error(f"Detection error: {error}")
 
    # ---------- Inline results (shown once a detection exists) ----------
    if "detected_image" in st.session_state:
 
        predictions = st.session_state["predictions"]
        total = st.session_state["box_count"]
        counts = Counter(p["class"] for p in predictions)
        weed_count = sum(n for name, n in counts.items()
                         if "weed" in name.lower())
        best = max((p["confidence"] for p in predictions), default=0)
        average = (sum(p["confidence"] for p in predictions) / total
                   if total else 0)
 
        st.markdown("""
        <div class="result-banner">
            <h3>✅ Detection completed successfully! 🌱</h3>
        </div>
        """, unsafe_allow_html=True)
 
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📦 Total detections", total)
        m2.metric("🌿 Weed detections", weed_count)
        m3.metric("🏆 Best confidence", f"{best:.0%}")
        m4.metric("📊 Average confidence", f"{average:.0%}")
 
        if total == 0:
            st.warning("No weeds found. Try lowering the confidence "
                       "threshold or uploading a clearer image.")
        elif weed_count > 0:
            st.error(f"⚠️ {weed_count} weed detection(s) found. "
                     "See the Weed Management tab for control methods.")
        else:
            st.success("🌾 No weeds detected in this image.")
 
        before, after = st.columns(2, gap="medium")
        with before:
            st.markdown("#### 📷 Original")
            st.image(st.session_state["original_image"],
                     use_container_width=True)
        with after:
            st.markdown("#### 🔍 Detected")
            st.image(st.session_state["detected_image"],
                     use_container_width=True)
 
        if predictions:
            with st.expander("📋 Detection details", expanded=False):
                st.dataframe(predictions, use_container_width=True)
 
        d1, d2 = st.columns(2, gap="medium")
        with d1:
            st.download_button(
                "⬇️ Download detected image",
                data=image_to_png_bytes(st.session_state["detected_image"]),
                file_name="greenguard_result.png",
                mime="image/png",
                use_container_width=True,
            )
        with d2:
            st.page_link(
                "pages/2_Detection_Results.py",
                label="🔍 View Full Detection Results",
                use_container_width=True,
            )
 
else:
    st.info("👆 Upload an image above to start weed detection.")
 
 
# ---------------- SESSION HISTORY ----------------
if st.session_state["history"]:
    st.divider()
    st.markdown("## 🕘 Recent Analyses")
    st.dataframe(
        list(reversed(st.session_state["history"])),
        use_container_width=True,
        hide_index=True,
    )
 
 
# ---------------- SIMPLE FOOTER ----------------
st.divider()
 
st.markdown("### 🌿 GreenGuard")
st.caption(
    "Deep Learning-Based Weed Detection System • "
    "Growing a greener future through smart agriculture"
)
 