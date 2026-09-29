# TB Follow-up Calculator — Android (Kivy)

Schedule:
- Month 2: treatment start date + 56 days
- Month 5: treatment start date + 140 days
- Month 6: treatment start date + 168 days

Features: patient name, patient ID, start date (DD-MM-YYYY), automatic
follow-up dates, offline storage, saved records, delete records.

## Build the APK (easiest, low data): GitHub Actions
1. Create a free GitHub repository.
2. Upload ALL files from this zip, keeping the folder
   .github/workflows/build.yml  (create it via "Add file > Create new file"
   if the upload skips hidden folders).
3. Open the Actions tab > "Build APK" > Run workflow.
4. After ~20-30 minutes download the "tb-followup-apk" artifact (zip
   containing the .apk) and install it on your phone.

## Build locally (Linux/WSL)
   pip install buildozer "cython<3"
   buildozer -v android debug
The APK appears in bin/.
