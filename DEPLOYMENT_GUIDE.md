# 🚀 Final Deployment Guide: AGEN-OHADA (Koyeb + Neon)

Follow these steps exactly to move your application from your computer to the cloud.

---

## Part 1: Database Setup (Neon.tech)
Neon provides a powerful PostgreSQL database with a permanent free tier.

1.  **Create Account**: Sign up at [Neon.tech](https://neon.tech/).
2.  **Create Project**: Create a new project named `agen-ohada`.
3.  **Get Connection String**: 
    - On the Dashboard, look for the **Connection Details** section.
    - Ensure "Pooled connection" is **unchecked** (for better compatibility with Flask).
    - Copy the string that looks like: `postgresql://alex:password@ep-cool-water-123.us-east-2.aws.neon.tech/neondb?sslmode=require`
    - **Save this link somewhere!** This is your `DATABASE_URL`.

---

## Part 2: App Hosting (Koyeb.com)
Koyeb will run your code inside the Docker container we created.

1.  **Create Account**: Sign up at [Koyeb.com](https://www.koyeb.com/).
2.  **Create Service**:
    - Click **"Create Service"**.
    - Choose **"GitHub"** as the source.
    - Select your repository: `MacoumbaFall/AGEN-OHADA-FLASK`.
3.  **Build Configuration**:
    - Set the **Build method** to **"Dockerfile"**. (Koyeb will automatically use the `Dockerfile` I created).
4.  **Environment Variables**:
    - Click **"Add Environment Variable"**.
    - Add the following:
        - `DATABASE_URL` = (Paste the link from Neon here)
        - `SECRET_KEY` = (Type a long random sentence like `MaSuperCleSecurte2025!`)
        - `FLASK_ENV` = `production`
        - `ADMIN_PASSWORD` = (The password you want for the admin account, e.g., `MonMotDePasse123`)
5.  **Expose Port**:
    - Ensure the "Exposed Port" is set to `8000` (which matches our Dockerfile).
6.  **Deploy**: Click **"Deploy"**.

---

## Part 3: Database Initialization (CRITICAL)
Your cloud database starts empty. You must run the setup script I created.

**Run this from your local computer terminal (VS Code):**
1.  Open your terminal.
2.  Run these two commands (replace the link with your actual Neon link):
    ```powershell
    $env:DATABASE_URL="postgresql://alex:password@ep-cool-water-123.us-east-2.aws.neon.tech/neondb?sslmode=require"
    python prod_setup.py
    ```
3.  **Wait for the success message**: It should say `DATABASE SETUP COMPLETE!`.

---

## Part 4: Verification
1.  Go to your Koyeb dashboard.
2.  Click on the **Public URL** provided (e.g., `https://agen-ohada-xxxx.koyeb.app/`).
3.  **Login**:
    - Username: `admin`
    - Password: (The one you set in Koyeb environment variables, or `admin123` if you didn't set one).
4.  **Test PDFs**: Go to the Accounting (Comptabilité) section and try to download a PDF. If it works, the Docker setup is successful!

---

### Troubleshooting
- **App is stuck on "Starting"**: Check the "Runtime Logs" in Koyeb. If it says "Database connection failed", verify your `DATABASE_URL`.
- **Changes didn't show up**: Koyeb redeploys every time you `git push`. Just push your changes and it will update automatically.
