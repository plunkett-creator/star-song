import Foundation
import StoreKit
import WebKit

/// In-app purchases, using StoreKit 2. Star Song sells one Non-Consumable product, the bundle,
/// whose ID is COLLECTION.bundleProductId in Web/pieces.js (starsong.bundle).
/// The store tells the collection page (window.__storeUpdate) the prices and which pieces are owned.
@MainActor
final class Store {
    weak var webView: WKWebView?
    private var products: [String: Product] = [:]
    private var owned: Set<String> = []
    private var updates: Task<Void, Never>?

    init() {
        // Purchases can also arrive from outside the app: Ask to Buy approvals, refunds,
        // or a purchase made on another device with the same Apple ID.
        updates = Task { [weak self] in
            for await result in Transaction.updates {
                if case .verified(let transaction) = result {
                    await transaction.finish()
                }
                await self?.refreshOwned()
                self?.push()
            }
        }
    }

    /// Fetch the prices for the paid pieces and check which of them are already owned.
    func load(ids: [String]) async {
        if !ids.isEmpty, let list = try? await Product.products(for: ids) {
            for product in list {
                products[product.id] = product
            }
        }
        await refreshOwned()
        push()
    }

    func buy(_ id: String) async {
        guard let product = products[id] else {
            push(message: "The collection isn't available right now. Please check your connection and try again.")
            return
        }
        do {
            // Apple asks UIKit-hosted apps to tie the purchase sheet to the app's window scene.
            let result: Product.PurchaseResult
            if #available(iOS 17.0, *), let scene = webView?.window?.windowScene {
                result = try await product.purchase(confirmIn: scene)
            } else {
                result = try await product.purchase()
            }
            switch result {
            case .success(let verification):
                if case .verified(let transaction) = verification {
                    await transaction.finish()
                    await refreshOwned()
                    push(message: "Thank you! \(product.displayName) is now yours.")
                } else {
                    push(message: "The purchase couldn't be verified. Please try Restore purchases.")
                }
            case .pending:
                push(message: "Your purchase is waiting for approval.")
            case .userCancelled:
                push()
            @unknown default:
                push()
            }
        } catch {
            push(message: "The purchase didn't go through. Please try again.")
        }
    }

    /// Restore purchases made earlier with the same Apple ID (App Review requires this button).
    func restore() async {
        do {
            try await AppStore.sync()
        } catch {
            // The person may have cancelled the sign-in; still report what we know.
        }
        await refreshOwned()
        push(message: owned.isEmpty
             ? "No earlier purchases were found for this Apple ID."
             : "Your collection has been restored.")
    }

    private func refreshOwned() async {
        var current = Set<String>()
        for await result in Transaction.currentEntitlements {
            if case .verified(let transaction) = result, transaction.revocationDate == nil {
                current.insert(transaction.productID)
            }
        }
        owned = current
    }

    /// Send prices, owned pieces and an optional message to the page that's showing.
    private func push(message: String? = nil) {
        var prices: [String: String] = [:]
        for (id, product) in products {
            prices[id] = product.displayPrice
        }
        var payload: [String: Any] = ["prices": prices, "owned": Array(owned)]
        if let message = message {
            payload["message"] = message
        }
        guard let data = try? JSONSerialization.data(withJSONObject: payload),
              let json = String(data: data, encoding: .utf8) else { return }
        webView?.evaluateJavaScript("window.__storeUpdate && window.__storeUpdate(\(json));", completionHandler: nil)
    }
}
