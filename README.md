# scanner-webapp


This webpage application aims to take a raw document image and provide a higher-quality scanned version.
This program does this by:
            
  - Detecting the edges of the document first.
  - Then, finding the contours that utilise a simple heuristic by assuming the largest contour with exactly four points is the document to be scanned.
  - Apply a perspective transform to obtain a top-down view of the document.

[Application is available here](https://scanner-webapp.streamlit.app/)
