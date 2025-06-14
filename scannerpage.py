import streamlit as st
from PIL import Image

st.header("Photo Scanner", divider="rainbow")

st.markdown('''
            By Jamie Tran
            
            Use this to scan your documents for a clearer view!
            
            This program does this by:
            
            - Detecting the edges of the document first.
            - Then finding the contours which utilises simple heuristic by assuming the largest contour with exactly four points is the document to be scanned.
            - Apply perspective transform to obtain a top-down view of the document.
            
            ''')

st.divider()
import pandas as pd
from io import StringIO
from transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
uploaded_file = st.file_uploader("Choose a JPG or PNG file to be scanned", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    # # To read file as bytes:
    # bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    # # To convert to a string based IO:
    # stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # # To read file as string:
    # string_data = stringio.read()
    # st.write(string_data)

    # # Can be used wherever a "file-like" object is accepted:
    # dataframe = pd.read_csv(uploaded_file)
    # st.write(dataframe)
    
     # Read image from uploaded file
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Resize and clone
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    # Grayscale, blur, edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Original (Resized)", channels="RGB")
    st.image(edged, caption="Edge Detection", channels="GRAY")

    # Find contours
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
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
    else:
        st.warning("Could not find document outline. Please try a clearer image.")