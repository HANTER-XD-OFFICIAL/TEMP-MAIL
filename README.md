# 📧 Mail Generator – Temporary Email Service

Powered by **MD RASEL**  
Developed by **MD RASEL**

---

## 📌 Project Overview

Mail Generator is a **client-side temporary / disposable email web application** built using **HTML, Tailwind CSS, and Vanilla JavaScript**.  
It uses the public **mail.tm API** to generate temporary email addresses and receive emails in real time.

Key features:
- Generate temporary email addresses
- Receive emails instantly
- Change or delete email manually
- Secure email viewing
- Session-based timer
- Light / Dark theme support

---

## 🧱 Technologies Used

- HTML5  
- Tailwind CSS (CDN)  
- Vanilla JavaScript (ES Modules)  
- mail.tm Public API  
- Google Fonts (Space Grotesk)  
- Material Symbols Icons  

---

## 🌐 External API Dependency

This project depends on the public API provided by **mail.tm**.

**API Base URL: https://api.mail.tm/**

Availability, rate limits, and email lifetime are controlled by mail.tm.

---

## ✉️ Email Generation Logic

1. Fetch available domains from mail.tm  
2. Generate random username  
3. Create temporary email account  
4. Request authentication token  
5. Store session in memory  

Email format: randomString@domain

---

## 🔄 Change & Delete Mail Behavior

### Change Mail
- Instantly generates a new email address
- Previous inbox session is stopped

### Delete Mail
- Deletes the current mail.tm account
- Automatically creates a new one

There is **no automatic time-based email rotation**.

---

## ⏳ Session Timer System

- Default duration: **10 minutes**
- Updates every second
- Extend button resets timer

When expired:
- Session marked as expired
- User prompted to extend or regenerate

---

## 📥 Inbox Refresh System

- Auto refresh every **10 seconds**
- Manual refresh button available
- Latest emails appear first

---

## 📩 Email Viewing

- Secure sandboxed iframe
- HTML rendering with fallback to text
- Safe and isolated environment

---

## 🗑 Message Deletion Notice

Delete Message button:
- Removes message from UI only
- Does **not** delete from server

---

## 🎨 Theme Support

- Light & Dark modes
- Preference stored in localStorage
- System theme detected automatically

---

## 🔐 Security Notes

- No backend server
- No database
- No permanent data storage
- Tokens stored only in runtime memory

---

## 👨‍💻 Developer

**Name:** MD RASEL  
**Branding:** Powered by MD RASEL  

<p align="left">
  <a href="https://www.facebook.com/MD.RASEL.8.2.3.4" target="_blank">
    <img src="https://img.shields.io/badge/Facebook-Profile-1877F2?style=for-the-badge&logo=facebook&logoColor=white" />
  </a>
</p>

---

## 📞 Contact

<p align="left">
  <a href="https://wa.me/8801882278234" target="_blank">
    <img src="https://img.shields.io/badge/WhatsApp-Chat-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" />
  </a>

  <a href="https://www.facebook.com/MD.RASEL.8.2.3.4" target="_blank">
    <img src="https://img.shields.io/badge/Facebook-Message-4267B2?style=for-the-badge&logo=messenger&logoColor=white" />
  </a>
</p>

---

## ⚠️ Disclaimer

This project is intended for **educational and personal use only**.  
Do not use temporary email services for illegal or abusive activities.

---

## ⬇️ Download

<p align="left">
  <a href="https://github.com/HANTER-XD-OFFICIAL/TEMP-MAIL/releases/tag/TEMP-MAIL_APK" target="_blank">
    <img src="https://img.shields.io/badge/Download-App-FF5722?style=for-the-badge&logo=android&logoColor=white" />
  </a>
</p>

> 🔧 **Note:**  
> Replace `https://github.com/HANTER-XD-OFFICIAL/TEMP-MAIL/releases/tag/TEMP-MAIL_APK` with your app download URL  
> (APK / Website / Play Store / Direct link)

---
## 🌍 Open Website

<p align="left">
  <a href="https://hanter-xd-official.github.io/TEMP-MAIL/" target="_blank">
    <img src="https://img.shields.io/badge/Open-Website-6200EA?style=for-the-badge&logo=googlechrome&logoColor=white" />
  </a>
</p>

---
