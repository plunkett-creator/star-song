package app.starsong

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.view.WindowManager
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.widget.FrameLayout
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewClientCompat
import org.json.JSONArray

/**
 * Star Song for Android: shows the shared collection and pieces (the app's assets are the Web folder)
 * full screen in a WebView, and sells the bundle through Google Play Billing (see Store.kt).
 */
class MainActivity : ComponentActivity() {

    private lateinit var web: WebView
    private lateinit var store: Store

    private val home = "https://appassets.androidplatform.net/assets/index.html"
    private val night = 0xFF060D22.toInt()

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Keep the screen awake while a piece plays, and hide the status and navigation bars.
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        WindowInsetsControllerCompat(window, window.decorView).apply {
            hide(WindowInsetsCompat.Type.systemBars())
            systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }

        // The pages are served from the app's own assets at a private https address.
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        web = WebView(this)
        web.setBackgroundColor(night)
        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            mediaPlaybackRequiresUserGesture = false
            allowFileAccess = false
            allowContentAccess = false
            setSupportZoom(false)
            builtInZoomControls = false
        }
        web.isVerticalScrollBarEnabled = false
        web.webViewClient = object : WebViewClientCompat() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? =
                loader.shouldInterceptRequest(request.url)

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val url = request.url
                if (url.host == "appassets.androidplatform.net") return false
                // Anything else (for example the privacy page or a store link) opens in the browser.
                try { startActivity(Intent(Intent.ACTION_VIEW, url)) } catch (_: Exception) {}
                return true
            }
        }

        store = Store(this) { js -> runOnUiThread { web.evaluateJavascript(js, null) } }
        web.addJavascriptInterface(Bridge(), "StarSongAndroid")

        // Keep pages clear of the camera cut-out; the page itself fills the rest of the screen.
        val frame = FrameLayout(this)
        frame.setBackgroundColor(night)
        frame.addView(web, FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))
        ViewCompat.setOnApplyWindowInsetsListener(frame) { v, insets ->
            val cut = insets.getInsets(WindowInsetsCompat.Type.displayCutout())
            v.setPadding(cut.left, cut.top, cut.right, cut.bottom)
            insets
        }
        setContentView(frame)

        // Back: from a piece, return to the collection; from the collection, leave the app.
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                val url = web.url ?: ""
                if (url.contains("/pieces/")) web.loadUrl("$home?home=1") else finish()
            }
        })

        if (savedInstanceState == null) web.loadUrl(home) else web.restoreState(savedInstanceState)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onPause() {
        web.evaluateJavascript("window.__ssHidden && window.__ssHidden(true)", null)
        web.onPause()
        super.onPause()
    }

    override fun onResume() {
        super.onResume()
        web.onResume()
        web.evaluateJavascript("window.__ssHidden && window.__ssHidden(false)", null)
        store.refresh()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) {
            WindowInsetsControllerCompat(window, window.decorView).hide(WindowInsetsCompat.Type.systemBars())
        }
    }

    override fun onDestroy() {
        store.close()
        web.destroy()
        super.onDestroy()
    }

    /** Called from the collection page (window.StarSongAndroid). These run on a background thread. */
    inner class Bridge {
        @JavascriptInterface
        fun products(idsJson: String) {
            val arr = JSONArray(idsJson)
            val ids = (0 until arr.length()).map { arr.getString(it) }
            runOnUiThread { store.load(ids) }
        }

        @JavascriptInterface
        fun buy(id: String) {
            runOnUiThread { store.buy(id) }
        }

        @JavascriptInterface
        fun restore() {
            runOnUiThread { store.restore() }
        }
    }
}
