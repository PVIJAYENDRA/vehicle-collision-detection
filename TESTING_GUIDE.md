# Testing Guide - How to Test Without Relevant Videos

## Quick Start Options

### Option 1: Use Your Existing Video (vv.mp4) ✅

You already have `vv.mp4`! Here's how to test with it:

#### Using GUI (Easiest):
```bash
python gui_app.py
```
Then:
1. Select "Video File"
2. Click "Browse / Select"
3. Choose `vv.mp4`
4. Click "Start Detection"

#### Using Command Line:
```bash
python run_detection.py --input vv.mp4 --type video
```

#### Quick Test Script:
```bash
python test_with_video.py
```

---

### Option 2: Use Live Camera Feed 📹

Test with your webcam in real-time:

#### Using GUI:
```bash
python gui_app.py
```
Then:
1. Select "Live Feed"
2. Set camera index (usually 0)
3. Click "Start Detection"

#### Using Command Line:
```bash
python run_detection.py --input 0 --type live
```

**Tip**: Point your camera at:
- Traffic outside your window
- Videos playing on another screen
- Toy cars moving on a table
- Any moving vehicles

---

### Option 3: Extract Frames from Your Video 🖼️

Convert your video to test images:

```bash
python test_with_video.py
# Choose option 3
```

This will extract frames from `vv.mp4` that you can test as images.

---

### Option 4: Create Synthetic Test Video 🎬

Generate a simple test video with moving shapes:

```bash
python download_test_videos.py
# Choose option 4
```

This creates `synthetic_test.mp4` with moving rectangles (simulating vehicles).

---

### Option 5: Download Sample Videos 📥

#### From YouTube:
1. Install yt-dlp:
   ```bash
   pip install yt-dlp
   ```

2. Download a traffic video:
   ```bash
   yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" -o sample_traffic.mp4
   ```

3. Search YouTube for:
   - "traffic video"
   - "driving video"
   - "highway traffic"
   - "city traffic"

#### Record Your Own:
- Use your phone to record traffic
- Record videos playing on screen
- Use screen recording software

---

## Step-by-Step Testing

### Test 1: Quick Test with Your Video

1. **Launch the test script:**
   ```bash
   python test_with_video.py
   ```

2. **Choose option 1 (GUI)** or **option 2 (CLI)**

3. **Watch the detection in action!**

### Test 2: Test with Live Feed

1. **Launch GUI:**
   ```bash
   python gui_app.py
   ```

2. **Select "Live Feed"**

3. **Set camera index to 0** (or try 1, 2 if 0 doesn't work)

4. **Click "Start Detection"**

5. **Point camera at:**
   - Traffic outside
   - Videos on screen
   - Moving objects

### Test 3: Extract and Test Images

1. **Extract frames:**
   ```bash
   python test_with_video.py
   # Choose option 3
   ```

2. **Test with GUI:**
   - Select "Image File"
   - Browse to `test_frames/` folder
   - Select any extracted frame
   - Click "Start Detection"

---

## What to Expect

### If Video Has Vehicles:
- ✅ Green boxes around detected vehicles
- ✅ Vehicle information (ID, speed, distance, angle)
- ✅ Trajectory lines showing movement
- ✅ Collision alerts if vehicles are close

### If Video Has No Vehicles:
- ℹ️ System will still run
- ℹ️ No detections will appear
- ℹ️ Information panel will show "No vehicles detected"

### If Using Live Feed:
- 📹 Real-time processing
- 📹 Continuous detection
- 📹 Live updates

---

## Troubleshooting

### "No vehicles detected"
- **Normal** if video has no vehicles
- Try pointing camera at traffic
- Try different videos
- Check if vehicles are visible and clear

### "Video file not found"
- Make sure `vv.mp4` is in the project folder
- Check file path is correct
- Verify file is not corrupted

### "Camera not working"
- Try different camera indices (0, 1, 2)
- Check if camera is used by another app
- Verify camera permissions

### "Model not loading"
- Check internet connection (first time download)
- Wait a few seconds
- Check disk space

---

## Testing Checklist

- [ ] Test with existing video (vv.mp4)
- [ ] Test with live camera feed
- [ ] Test with extracted images
- [ ] Test GUI interface
- [ ] Test command line interface
- [ ] Verify vehicle detection works
- [ ] Check collision alerts
- [ ] Review vehicle information panel

---

## Tips for Better Testing

1. **Use Clear Videos**: Videos with clear, visible vehicles work best

2. **Good Lighting**: Ensure good lighting in videos/feed

3. **Stable Camera**: Use stable camera for live feed

4. **Multiple Angles**: Try videos from different angles

5. **Different Speeds**: Test with slow and fast-moving vehicles

---

## Next Steps

Once testing works:
1. Try with your own videos
2. Adjust detection parameters in `config.py`
3. Test with different camera angles
4. Experiment with collision thresholds

---

## Quick Commands Reference

```bash
# Test with your video
python test_with_video.py

# Launch GUI
python gui_app.py

# Test video via CLI
python run_detection.py --input vv.mp4

# Test live feed
python run_detection.py --input 0

# Create synthetic video
python download_test_videos.py
```

---

## Need Help?

- Check `vv.mp4` exists in project folder
- Try live feed if video doesn't work
- Extract frames for image testing
- Create synthetic video for basic testing

**Remember**: Even if your video doesn't have vehicles, the system will still run and show "No vehicles detected" - this is normal!


