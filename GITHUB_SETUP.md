# GitHub Setup Guide

## Step-by-Step Instructions to Push Project to GitHub

### Prerequisites
- Git installed on your system
- GitHub account created
- GitHub repository created (empty repository)

---

## Step 1: Initialize Git Repository (if not already initialized)

```bash
cd "c:\Users\vijay\Downloads\BASED PROJECT"
git init
```

---

## Step 2: Add All Files to Git

```bash
git add .
```

**Note**: This will add all files except those in `.gitignore`:
- Python cache files (`__pycache__/`)
- Virtual environments (`venv/`, `env/`)
- Large model files (yolov8s.pt, yolov8m.pt, etc.)
- Test videos (`synthetic_test.mp4`, `test_*.mp4`)
- IDE files (`.vscode/`, `.idea/`)

---

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Vehicle Collision Detection System with YOLOv8"
```

Or with more details:
```bash
git commit -m "Initial commit: Vehicle Collision Detection System

- YOLOv8-based real-time vehicle detection
- Multi-view monitoring (front, back, left, right)
- Kalman filter tracking with speed calculation
- Multi-factor collision prediction (distance, speed, angle)
- GUI and CLI interfaces
- Support for image, video, and live feed inputs"
```

---

## Step 4: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon in the top right
3. Select **"New repository"**
4. Fill in:
   - **Repository name**: `vehicle-collision-detection` (or your preferred name)
   - **Description**: "Real-time vehicle collision detection system using YOLOv8 and Kalman filtering"
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

---

## Step 5: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/vehicle-collision-detection.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/vehicle-collision-detection.git
```

**Example**:
```bash
git remote add origin https://github.com/vijay/vehicle-collision-detection.git
```

---

## Step 6: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

If you get authentication error, you may need to:
- Use GitHub Personal Access Token instead of password
- Or set up SSH keys

---

## Step 7: Verify Upload

1. Go to your GitHub repository page
2. Refresh the page
3. You should see all your files uploaded

---

## Alternative: Using GitHub CLI (if installed)

```bash
# Login to GitHub
gh auth login

# Create repository and push
gh repo create vehicle-collision-detection --public --source=. --remote=origin --push
```

---

## Files That Will Be Uploaded

✅ **Will be uploaded**:
- All Python source files (`.py`)
- Configuration files (`config.py`)
- Documentation (`.md` files)
- Requirements file (`requirements.txt`)
- YOLOv8 model (`yolov8n.pt` - small model)
- Your video files (`DEMO2.mp4`, `vv.mp4`)

❌ **Will NOT be uploaded** (due to `.gitignore`):
- `__pycache__/` folders
- Virtual environments
- Large model files (yolov8s.pt, yolov8m.pt, etc.)
- Test videos (`synthetic_test.mp4`)
- IDE configuration files

---

## Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### Error: Authentication failed
- Use GitHub Personal Access Token instead of password
- Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Error: "large file detected"
If you have large video files (>100MB), GitHub may reject them. Options:
1. Use Git LFS (Large File Storage)
2. Remove large files from commit
3. Upload videos separately or use external storage

### To remove large files from Git history:
```bash
git rm --cached DEMO2.mp4  # Remove from Git but keep local file
git commit -m "Remove large video file"
```

---

## Quick Commands Summary

```bash
# 1. Initialize (if needed)
git init

# 2. Add files
git add .

# 3. Commit
git commit -m "Initial commit: Vehicle Collision Detection System"

# 4. Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 5. Push
git branch -M main
git push -u origin main
```

---

## Repository Settings Recommendations

After pushing, consider:

1. **Add Topics/Tags**: 
   - `computer-vision`
   - `yolov8`
   - `vehicle-detection`
   - `collision-detection`
   - `kalman-filter`
   - `python`
   - `opencv`

2. **Add Description**: 
   "Real-time vehicle collision detection system using YOLOv8 deep learning and Kalman filtering for multi-view monitoring"

3. **Enable GitHub Pages** (optional): For documentation

4. **Add License**: MIT License recommended for open source

5. **Add Badges** (optional): Add to README.md
   ```markdown
   ![Python](https://img.shields.io/badge/Python-3.8+-blue)
   ![YOLOv8](https://img.shields.io/badge/YOLOv8-8.0+-green)
   ![License](https://img.shields.io/badge/License-MIT-yellow)
   ```

---

## Next Steps After Upload

1. **Add README badges** (optional)
2. **Create releases** for version tags
3. **Add issues template** for bug reports
4. **Add pull request template** for contributions
5. **Create GitHub Actions** for CI/CD (optional)

---

## Need Help?

- Git documentation: https://git-scm.com/doc
- GitHub documentation: https://docs.github.com
- Git commands cheat sheet: https://education.github.com/git-cheat-sheet-education.pdf

