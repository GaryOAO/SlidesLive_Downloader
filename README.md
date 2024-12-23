# 📥 **SlidesLive Downloader**

A **fast** and **efficient** tool to download presentations from **SlidesLive** and convert them to **PDF** format.

---

## 🚀 **Features**

- **💨 Multi-threaded downloading** for blazing-fast speeds
- **🔄 Automatic retry** mechanism for failed downloads
- **📊 Real-time progress tracking** during the download
- **🎨 High-quality slide downloads** (1080p)
- **📄 Automatic PDF conversion** from slides
- **⚡ Simple, user-friendly command-line interface**

---

## ⚡ **Quick Start**

### 1. **Install Dependencies**
To get started, first install the necessary dependencies:

```bash
pip install -r requirements.txt
```

### 2. **Basic Usage**
Download a presentation and convert it to a PDF by running the script:

```bash
python slide_download.py <slideslive_url>
```

### 3. **Custom Output Directory**
If you want to specify a custom output directory for the downloaded slides and the generated PDF, simply add the path:

```bash
python slide_download.py <slideslive_url> /path/to/output
```

---

## 💡 **Examples**

**Download a presentation:**

```bash
python slide_download.py https://slideslive.com/39006337
```

The script will automatically:

1. Extract the presentation ID from the URL
2. Download all slides in parallel using multi-threading
3. Convert them into a single PDF file
4. Clean up temporary files

---

## 🛠️ **Requirements**

- Python 3.6 or higher
- An active **internet connection**
- Check `requirements.txt` for required Python packages

---

## 📜 **License**

This project is licensed under the [MIT License](LICENSE).

---

We welcome **issues** and **pull requests**! If you have suggestions or improvements, feel free to fork the repo and submit a PR.

Happy coding! 👩‍💻👨‍💻