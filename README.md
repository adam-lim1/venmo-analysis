# venmo-analysis

Gain insight into a Venmo user's spending behavior via LDA topic modeling.

Components:
- Scrape.py - Scrape Venmo API for transaction information
- CleanVenmoData.py - Preprocess scraped data (remove stop words, stem, words, translate emojis, get user pictures)
- FacialRecognition.py - Set up AWS collection for facial recognition
- Query.py - Capture webcam image of user and use to query database for transactions; get insights from user transactions
