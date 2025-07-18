import streamlit as st
from PIL import Image
from transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import cv2
import imutils
import io
from PIL import Image

# Page config
st.set_page_config(
    page_title="Document Scanner",
    page_icon="📄",
    layout="wide"
)

st.header("📄 Document Scanner", divider="rainbow")

# Sidebar for settings
st.sidebar.header("⚙️ Settings")

output_format = st.sidebar.selectbox(
    "Output Format",
    ["PNG", "PDF", "JPEG"]
)


st.markdown('''
**By Jamie Tran**

Transform your photos into clean, professional scanned documents!

**Features:**
- 🎯 Automatic document detection
- 📐 Perspective correction
- 📱 Mobile-friendly interface
- 💾 Multiple output formats

**How it works:**
1. Edge detection to find document boundaries
2. Contour analysis to identify the document outline
3. Perspective transformation for a top-down view
4. Image enhancement for clarity
''')

# Input method selection
input_method = st.radio(
    "📱 Choose input method:",
    ["Upload File", "Take Photo"],
    horizontal=True
)

current_file = None

if input_method == "Upload File":
    # File upload with drag and drop
    current_file = st.file_uploader(
        "📁 Choose an image file to scan",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, PNG, JPEG"
    )
else:  # Take Photo
    # Camera input option
    current_file = st.camera_input("📸 Take a photo of your document")

# # Use camera image if available, otherwise use uploaded file
# current_file = camera_image if camera_image is not None else uploaded_file
if current_file is not None:
    
     # Read image from uploaded file
    file_bytes = np.asarray(bytearray(current_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Resize and clone
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    # Grayscale, blur, edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # convert to grayscale
    gray = cv2.GaussianBlur(gray, (5, 5), 0) # reduce noise
    edged = cv2.Canny(gray, 75, 200) # find edges

    st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Original (Resized)", channels="RGB")
    st.image(edged, caption="Edge Detection", channels="GRAY")

    # Find contours
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) # finds closed shapes
    cnts = imutils.grab_contours(cnts) # largest contours -> document likely to be largest
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5] 

    screenCnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True) # calculate perimeter
        approx = cv2.approxPolyDP(c, 0.02 * peri, True) # approximate shape
        if len(approx) == 4: # find 4 sided shape
            screenCnt = approx
            break

    if screenCnt is not None:
        cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Detected Outline", channels="RGB")

        # Transform and threshold
        warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        T = threshold_local(warped, 11, offset=10, method="gaussian")
        warped = (warped > T).astype("uint8") * 255

        st.image(warped, caption="Scanned", channels="GRAY")
        scanned_pil = Image.fromarray(warped)

        # Save to a BytesIO buffer
        buf = io.BytesIO()
        
        if output_format == "PDF":
            scanned_pil.save(buf, format="PDF")
            mime_type = "application/pdf"
            file_extension = "pdf"
            
        elif output_format == "JPEG":
            scanned_pil.save(buf, format="JPEG", quality=95)
            mime_type = "image/jpeg"
            file_extension = "jpg"
            
        else:  # PNG
            scanned_pil.save(buf, format="PNG")
            mime_type = "image/png"
            file_extension = "png"
        byte_im = buf.getvalue()

        # Add download button
        st.download_button(
            label=f"📥 Download Scanned Document ({output_format})",
            data=byte_im,
            file_name=f"scanned_document.{file_extension}",
            mime="mime_type",
            use_container_width=True
        )
        st.info(f"📊 **File Info:** {output_format} format | Size: {len(byte_im)/1000} KB")
    else:
        st.warning("Could not find document outline. Please try a clearer image.")
        
# Footer with tips
st.divider()
with st.expander("💡 Tips for Best Results"):
    st.markdown("""
    **Photography Tips:**
    - Use good, even lighting
    - Place document on a dark, contrasting background
    - Ensure all four corners of the document are visible
    - Hold camera steady and parallel to the document
    - Avoid shadows and glare

    """)