import SwiftUI
import WebKit
import AVFoundation

/// Star Song: a collection of night-sky sound pieces. Each piece is a bundled web page under Web/pieces/<id>/,
/// listed in Web/pieces.js, and Web/index.html is the collection screen. Wandering Stars is free;
/// the rest are unlocked by one in-app purchase, the bundle (see Store.swift).
@main
struct StarSongApp: App {
    @Environment(\.scenePhase) private var phase

    init() {
        // Play through the speaker even when the ring/silent switch is on, like any instrument app.
        try? AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
    }

    var body: some Scene {
        WindowGroup {
            CollectionView()
                .ignoresSafeArea()
                .background(Color(red: 6 / 255, green: 13 / 255, blue: 34 / 255).ignoresSafeArea())
                .statusBarHidden(true)
                .persistentSystemOverlays(.hidden)
        }
        .onChange(of: phase) { newPhase in
            // Keep the screen awake while a piece is open, so it can play on a table like a music box.
            UIApplication.shared.isIdleTimerDisabled = (newPhase == .active)
            if newPhase == .active {
                try? AVAudioSession.sharedInstance().setActive(true)
            }
        }
    }
}

struct CollectionView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        config.userContentController.add(context.coordinator, name: "haptic")
        config.userContentController.add(context.coordinator, name: "store")

        let web = WKWebView(frame: .zero, configuration: config)
        let night = UIColor(red: 6 / 255, green: 13 / 255, blue: 34 / 255, alpha: 1)
        web.isOpaque = false
        web.backgroundColor = night
        web.scrollView.backgroundColor = night
        web.scrollView.bounces = false
        web.scrollView.contentInsetAdjustmentBehavior = .never
        web.allowsLinkPreview = false
        web.allowsBackForwardNavigationGestures = false
        web.navigationDelegate = context.coordinator
        context.coordinator.store.webView = web

        if let page = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "Web") {
            // Read access covers the whole Web folder, so the collection and every piece can load.
            web.loadFileURL(page, allowingReadAccessTo: page.deletingLastPathComponent())
        }
        return web
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}

    @MainActor
    final class Coordinator: NSObject, WKScriptMessageHandler, WKNavigationDelegate {
        let store = Store()
        private let impact = UIImpactFeedbackGenerator(style: .soft)

        func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
            switch message.name {
            case "haptic":
                // A soft tap under the finger, e.g. when you throw a comet.
                impact.impactOccurred(intensity: 0.7)
            case "store":
                guard let body = message.body as? [String: Any], let action = body["action"] as? String else { return }
                let store = self.store
                switch action {
                case "products":
                    let ids = body["ids"] as? [String] ?? []
                    Task { await store.load(ids: ids) }
                case "buy":
                    if let id = body["id"] as? String { Task { await store.buy(id) } }
                case "restore":
                    Task { await store.restore() }
                default:
                    break
                }
            default:
                break
            }
        }

        // Pages are swapped as you move between the collection and a piece: keep the page's
        // scrolling off inside a piece (the collection screen scrolls when it holds many pieces).
        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            let inPiece = webView.url?.path.contains("/pieces/") ?? false
            webView.scrollView.isScrollEnabled = !inPiece
        }

        // If iOS reclaims the page's memory while the app is in the background, start it again.
        func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
            webView.reload()
        }
    }
}
