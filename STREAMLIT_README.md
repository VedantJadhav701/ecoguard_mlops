# EcoGuard Streamlit Dashboard

Interactive web UI for testing all EcoGuard ML models via the live Render API.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-streamlit.txt
```

### 2. Run Streamlit App
```bash
streamlit run streamlit_app.py
```

The app will open at: **http://localhost:8501**

## 📱 Features

### 🎯 Vision Detection (Tab 1)
- Upload images to detect waste objects
- Uses YOLOv8 model
- Shows detected items with confidence scores
- Real-time detection

### ⚖️ Weight Estimation (Tab 2)
- Select material type (plastic, glass, metal, paper, cardboard, trash)
- Adjust item size percentage
- Get estimated weight in grams
- Shows weight range

### 🌱 Carbon Calculator (Tab 3)
- Calculate CO₂ emissions for any waste material
- Compare recycled vs non-recycled impact
- Shows environmental impact
- Provides recycling recommendations

### 📊 Lifestyle Tracker (Tab 4)
- Track personal carbon footprint
- Customize energy, transportation, food habits
- See annual CO₂ emissions
- Get personalized recommendations
- Compare to average person

## 🔗 API Connection

The app connects to your live Render API:
```
https://ecoguard-mlops.onrender.com
```

**Note:** First request may take 30-60 seconds as the free tier service wakes up.

## 🎯 Deployment Options

### Option 1: Streamlit Cloud (Easiest)
1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Click "New app"
4. Select your GitHub repo and `streamlit_app.py`
5. Deploy! 🚀

### Option 2: Docker
```bash
docker build -f Dockerfile.streamlit -t ecoguard-streamlit .
docker run -p 8501:8501 ecoguard-streamlit
```

### Option 3: Local Development
```bash
streamlit run streamlit_app.py
```

## 📊 Features Breakdown

| Feature | Status | API Endpoint |
|---------|--------|-------------|
| Vision Detection | ✅ Fully Functional | `/api/vision/detect` |
| Weight Estimation | ✅ Fully Functional | `/api/weight/estimate` |
| Carbon Calculation | ✅ Fully Functional | `/api/carbon/calculate` |
| Lifestyle Tracking | ✅ Fully Functional | `/api/lifestyle/predict` |
| Health Check | ✅ Fully Functional | `/health` |

## 🔧 Customization

### Change API URL
Edit `streamlit_app.py` line 23:
```python
API_BASE_URL = "your_custom_url"
```

### Add New Features
- Edit the tabs in `streamlit_app.py`
- Add new requests to API endpoints
- Use Streamlit components for UI

## 📈 Performance

- **Loading Time**: < 3 seconds (after first request)
- **Image Detection**: 30-60 seconds (first time only)
- **Weight Calculation**: < 1 second
- **Carbon Calculation**: < 1 second
- **Lifestyle Analysis**: < 2 seconds

## 🐛 Troubleshooting

### "API not responding"
- The free Render tier service may sleep after 15 minutes of inactivity
- Click a button again to wake it up (30-60 second startup)

### "Connection refused"
- Make sure your internet is connected
- Check that https://ecoguard-mlops.onrender.com/health is accessible
- Try in incognito mode (no cache issues)

### "File upload not working"
- Use .jpg, .jpeg, .png, or .bmp images
- File size should be < 25MB
- Check browser console for errors

## 📚 Additional Resources

- **API Docs**: https://ecoguard-mlops.onrender.com/docs
- **GitHub**: https://github.com/VedantJadhav701/ecoguard_mlops
- **Streamlit Docs**: https://docs.streamlit.io
- **Render Docs**: https://render.com/docs

## 🎯 Next Steps

1. **Test Locally**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Deploy to Streamlit Cloud** (5 minutes)
   - Push to GitHub
   - Connect to Streamlit Cloud
   - Done! 🚀

3. **Share with Others**
   - Get public URL from Streamlit Cloud
   - Share in team Slack/email

## 📝 License

MIT License - See LICENSE file

---

**Questions?** Check the [main README](README.md) or [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
