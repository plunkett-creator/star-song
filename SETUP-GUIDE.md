# Star Song: getting it onto the App Store, Google Play and the web

Everything is in one GitHub repository and is built on GitHub's computers, so you never need a Mac or Android Studio. Three "workflows" do the work:

| Workflow (Actions tab) | What it does |
|---|---|
| **Website - publish** | Puts the website online (free, with GitHub Pages). Runs by itself whenever the `Web` folder changes. |
| **iPhone app - build and upload** | Builds the iPhone/iPad app and uploads it to App Store Connect. |
| **Android app - build** | Builds the Android app as an `.aab` file for you to upload to Google Play. |

The pieces themselves live once, in `Web/`, and all three use them. Screenshots, icons and listing text for the stores are in the separate `star-song-store-assets.zip`. Keep that on your PC; it doesn't go on GitHub.

**Rough costs:** Apple Developer Program about £79 a year; Google Play $25 once; GitHub and the website free.
**Rough timings:** the website takes an evening. Apple usually approves a new account in 1–2 days and reviews the app in 1–3 days. Google needs **14 days of testing with 12 testers** before a new personal account can publish (Part C, step 6).

---

## Part A: GitHub and the website (do this first)

1. Make a free account at **github.com**.
2. Click **+** > **New repository**. Name it `star-song`, choose **Public**, tick **Add a README file**, and click **Create repository**.
   - It must be public for the free website. Your keys are kept as hidden "secrets", never in the files.
3. Upload the project in **two goes**, because GitHub's upload page takes at most 100 files at a time. Unzip `star-song.zip` and open the `star-song` folder.
   - **First go:** click **Add file** > **Upload files**. Select everything in the folder **except `Web`** (including the `.github` folder) and drag it onto the page. When the upload finishes, click **Commit changes**.
   - **Second go:** click **Add file** > **Upload files** again and drag in the **`Web`** folder on its own. Then click **Commit changes**.
   - If no `.github` folder appears in the repository afterwards, turn on **View > Show > Hidden items** in File Explorer and drag `.github` in on its own.
4. Put your email address in the privacy policy: in the repository, open `Web/privacy.html`, click the pencil, replace both `you@example.com`, and click **Commit changes**.
5. Turn on the website: **Settings** > **Pages** > under *Build and deployment*, set **Source** to **GitHub Actions**.
6. **Actions** tab > enable workflows if asked > **Website - publish** > **Run workflow**. About a minute later your site is live at
   `https://YOUR-GITHUB-NAME.github.io/star-song/`
   - The privacy page is at `.../star-song/privacy.html`. Both stores need this link.
   - Link the site from your YouTube channel and video descriptions.

## Part B: iPhone and iPad (App Store)

1. **Join the Apple Developer Program** at developer.apple.com/programs/enroll as an **Individual** (about £79 a year), and wait for the confirmation email.
2. **Register the bundle ID:** developer.apple.com/account > **Certificates, IDs & Profiles** > **Identifiers** > **+** > **App IDs** > **App**. Description `Star Song`; Explicit bundle ID such as `com.yourname.starsong` (lower case, permanent).
3. **Create the app:** appstoreconnect.apple.com > **Apps** > **+** > **New App**. iOS; Name **Star Song** (if taken, *Star Song: Night Sky Music*); English (U.K.); your bundle ID; SKU `starsong1`.
4. **Agreements for selling:** App Store Connect > **Business** > accept the **Paid Apps Agreement** and add bank and tax details. Also join the **Small Business Program** (Apple then takes 15% rather than 30%).
5. **Create the in-app purchase:** your app > **Monetization** > **In-App Purchases** > **+**:
   Type **Non-Consumable**; Reference name `Star Song collection`; Product ID exactly **`starsong.bundle`**; price (e.g. £3.99); display name *The Star Song collection* with the description from `store-assets/listing.md`; a review screenshot (use `store-assets/iphone-6.9in-1-collection.png`).
6. **API key:** **Users and Access** > **Integrations** > **App Store Connect API** > **Team Keys** > **+**. Name `GitHub`, Access **Admin**. **Download** the `.p8` file (only possible once), and note the **Key ID** and **Issuer ID**.
7. **Certificate key:** open **PowerShell** and paste the line below. When it asks for a passphrase, press **Enter** twice.
   ```
   ssh-keygen -t rsa -b 2048 -m PEM -f "$HOME\Desktop\ios_cert_key"
   ```
8. **GitHub secrets:** repository **Settings** > **Secrets and variables** > **Actions**:
   - **Secrets** tab, New repository secret:
     - `ASC_ISSUER_ID`: the Issuer ID
     - `ASC_KEY_ID`: the Key ID
     - `ASC_PRIVATE_KEY`: everything in the `.p8` file (open it in Notepad)
     - `CERTIFICATE_PRIVATE_KEY`: everything in `ios_cert_key` on your Desktop (the one without `.pub`)
   - **Variables** tab: `BUNDLE_ID` = your bundle ID from step 2.
9. **Build:** **Actions** > **iPhone app - build and upload** > **Run workflow**. About 15 minutes later, a green tick means it's uploaded. Apple then processes it for 10–30 minutes, and it appears under **TestFlight**.
10. **Test on your iPhone:** TestFlight tab > **Internal Testing** > add yourself, then install Apple's **TestFlight** app. Purchases there are free test purchases. Check that you can buy the collection, open every piece, and use **Restore purchases** after reinstalling.
11. **Submit:** fill in the version page with the text and screenshots in `store-assets/`, choose the build, and under **In-App Purchases** add `starsong.bundle`. Set **App Privacy** to "Data not collected", add the privacy URL, then **Add for Review** > **Submit**.

## Part C: Android (Google Play)

1. **Make a developer account** at **play.google.com/console** ($25 once). Choose a **personal** account and complete the identity check.
2. **Create the app:** **Create app**. Name **Star Song**, default language English (UK), **App**, **Free**, then accept the declarations.
3. **Choose your package name.** This is Android's permanent ID, e.g. `com.yourname.starsong`. You set it in GitHub, not in the Console:
   - Repository **Settings** > **Secrets and variables** > **Actions** > **Variables** tab: `ANDROID_PACKAGE` = your package name.
4. **Signing key:** I've made your Android upload key. Follow `ANDROID-SIGNING-KEY.txt` (sent separately) to add the four `ANDROID_*` secrets. Keep that file and `starsong-upload.jks` backed up somewhere private. Don't put them in the repository.
5. **Build:** **Actions** > **Android app - build** > **Run workflow**. When it's green, open the run and download **StarSong-android-N** at the bottom. Unzip it to get the `.aab` file.
6. **Closed test (required for new personal accounts):**
   - Play Console > **Test and release** > **Testing** > **Closed testing** > **Create track** > **Create new release**.
   - Upload the `.aab`, and accept **Play App Signing** when asked. Then save and send the release for review.
   - Under **Testers**, add an email list of **at least 12 people** with Android phones (their Google account emails), and share the opt-in link with them.
   - They must install the app and stay signed up for **14 days in a row**. Ask them to open it now and then. After that, Play Console lets you **apply for production access**.
7. **In-app product:** once the first upload exists, go to **Monetize** > **Products** > **One-time products** > **Create**. Product ID exactly **`starsong.bundle`**, with the name, description and price from `listing.md`. Activate it. You'll also need a **payments profile** (Monetize setup) to sell.
   - In the closed test, add yourself under **Settings** > **License testing** to make free test purchases.
8. **Store listing:** **Grow** > **Store presence** > **Main store listing**. Paste the text and upload the icon, feature graphic and `android-phone-*` screenshots from `store-assets/`. Under **App content**: privacy policy URL; Data safety: no data collected or shared; Ads: none; target audience: adults/everyone; content rating questionnaire: all "no".
9. When production access is granted: **Production** > **Create new release** > choose the same build (or upload a newer one) > **Review** > **Start rollout**.

## Part D: once the apps are live

Open `Web/pieces.js` on GitHub, click the pencil, and paste the store links into `appStoreUrl` and `playStoreUrl`. Commit, and the website will show **App Store** and **Google Play** buttons, including at the end of each one-minute taste.

---

### When something goes wrong
A red cross in Actions means a step failed: click into it, open the red step, and copy the last lines of the log to me. Most first-time failures are a mistyped secret, or a bundle ID or package name that doesn't match.
