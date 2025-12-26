# Quick Guide: Push Project to GitHub

## Step-by-Step Commands

### 1. Navigate to Project Folder
```bash
cd "c:\Users\vijay\Downloads\BASED PROJECT"
```

### 2. Initialize Git (if not already done in this folder)
```bash
git init
```

### 3. Add All Project Files
```bash
git add .
```

### 4. Create Initial Commit
```bash
git commit -m "Initial commit: Vehicle Collision Detection System with YOLOv8"
```

### 5. Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `vehicle-collision-detection` (or your choice)
3. Description: "Real-time vehicle collision detection using YOLOv8 and Kalman filtering"
4. Choose Public or Private
5. **DO NOT** check "Initialize with README"
6. Click "Create repository"

### 6. Connect and Push
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/vehicle-collision-detection.git
git branch -M main
git push -u origin main
```

---

## Complete Command Sequence

Copy and paste these commands (replace YOUR_USERNAME):

```bash
cd "c:\Users\vijay\Downloads\BASED PROJECT"
git init
git add .
git commit -m "Initial commit: Vehicle Collision Detection System"
git remote add origin https://github.com/YOUR_USERNAME/vehicle-collision-detection.git
git branch -M main
git push -u origin main
```

---

## Important Notes

- **Large Files**: If DEMO2.mp4 is very large (>100MB), GitHub may reject it
- **Authentication**: You may need to use a Personal Access Token instead of password
- **Video Files**: Consider using Git LFS for large videos or excluding them

---

## If You Get Authentication Error

Use GitHub Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select `repo` scope
4. Copy token and use it as password when pushing

